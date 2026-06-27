# Design: test suite for `index.py`

**Date:** 2026-06-27
**Status:** approved (brainstorming)

## Goal

Give `index.py` (the convention's validator + index generator) a real automated
test suite, aligned with the testing conventions of the
`fastapi-sqlalchemy-template` reference repo. The repo currently has zero Python
tooling — no `pyproject.toml`, no `tests/`, no `Justfile` — and CI runs inline
`python` smoke tests. This work introduces the full `uv` + `pytest` +
`pytest-cov` (100%) + `ruff`/`ty` stack, refactors `index.py` for testability,
rewires CI, and bumps the convention version.

## Constraints & decisions

- **Test infra:** full template alignment — `uv`, `pytest`, `pytest-cov` at 100%
  coverage, `ruff` (`select = ALL`), `ty`, with `dev`/`lint` dependency groups.
- **`index.py` testability:** refactor to thread an explicit `root` path rather
  than module-level `__file__`-derived constants. (User chose refactor over
  test-side monkeypatching.)
- **`main` shape:** `main(argv=None, root=None)` so both CLI modes are unit
  testable without monkeypatching `sys.argv`.
- **Python version:** `requires-python = ">=3.10,<4"`, ruff `target-version =
  "py310"` — the lowest across the modern-python org (matches `modern-di`), so
  `index.py` stays portable to the lowest python a consumer repo might run.
- **Version bump:** patch → `1.1.1` (behavior-preserving refactor; consumer CLI
  usage unchanged). Git tag created as the final step.
- **Behavior invariant:** the refactor must preserve identical stdout, identical
  violation strings, and identical exit codes. This is asserted by test.

## 1. `index.py` refactor

Thread a `root: pathlib.Path` through the directory-reading functions; keep all
regex/required-key constants module-level.

- Module default: `ROOT = pathlib.Path(__file__).parent`.
- Remove the `CHANGES_DIR` / `DECISIONS_DIR` module constants. Each reader
  derives `root / "changes"` and `root / "decisions"` internally.
- New / changed signatures:
  - `load_bundles(root: pathlib.Path) -> list[dict[str, str]]`
  - `load_decisions(root: pathlib.Path) -> list[dict[str, str]]`
  - `check(root: pathlib.Path) -> list[str]`
  - `main(argv: list[str] | None = None, root: pathlib.Path | None = None) -> int`
    — defaults: `argv = sys.argv[1:]`, `root = ROOT`. Reads `"--check" in argv`.
- Unchanged: `parse_frontmatter`, `_named`, `format_row`, `render`, `_require`,
  `_check_spec_file`, `_check_bundle`, `_check_decision`, and every regex /
  required-key constant.
- `path` fields in rows stay repo-relative (`changes/<name>/<file>`,
  `decisions/<file>`) — unchanged.
- Keep the inline `# ruff: noqa: INP001, D212` header — it is meaningful in the
  consumer location (`planning/index.py`, also not a package).
- `if __name__ == "__main__": raise SystemExit(main())` stays.

## 2. Test suite (`tests/`)

Pure-stdlib target ⇒ fast, fixture-driven tests using `tmp_path`. Target 100%
coverage (enforced by `--cov-fail-under=100`). Type-annotate all test args; no
docstrings required; `assert` allowed (`S101` ignored for `tests/*`).

- `tests/conftest.py` — small helpers to write a bundle dir
  (`design.md`/`change.md`/`plan.md`) and a decision file under a `tmp_path`
  root.
- `tests/test_parse_frontmatter.py`
  - empty input / no leading `---` → `{}`
  - normal single-line-scalar block
  - `null` value → empty string
  - single- and double-quoted values stripped
  - line without `": "` separator skipped
  - space- and tab-indented continuation lines skipped
  - second `---` terminates the block
- `tests/test_load.py`
  - `load_bundles`: `design.md` preferred over `change.md`; `change.md`
    fallback; bundle with neither skipped; non-dir entries skipped; missing
    `changes/` dir → `[]`; `date`/`slug` derived from dir name; `path`/`name`
    populated.
  - `load_decisions`: reads frontmatter; `README.md` and `_`-prefixed files
    skipped; missing `decisions/` dir → `[]`; `date`/`slug` derived from file
    name.
- `tests/test_check.py` — one assertion per violation branch plus the clean case:
  - bundle dir name not `YYYY-MM-DD.NN-slug`
  - unexpected file in bundle
  - bundle with neither `design.md` nor `change.md`
  - spec missing / empty `summary`
  - decision file name not `YYYY-MM-DD-slug`
  - decision missing `status` / `summary`
  - decision invalid `status`
  - valid tree → `[]`
- `tests/test_render.py`
  - `format_row`: with `supersedes`, with `superseded_by`, with both, and the
    `(no summary)` fallback
  - `render`: newest-first ordering for changes and decisions; `_None._` for
    empty sections; stable known-fixture snapshot (the behavior invariant).
- `tests/test_main.py`
  - `main([], root=...)` prints the index, returns `0` (capture stdout)
  - `main(["--check"], root=...)` on a clean tree → `0`, stdout `planning: OK`
  - `main(["--check"], root=...)` on a dirty tree → `1`, violations on stderr
  - `runpy.run_path(str(INDEX_PATH), run_name="__main__")` inside
    `pytest.raises(SystemExit)` to cover the `__main__` guard (mirrors the
    reference repo's `runpy` usage).

## 3. Repo tooling

### `pyproject.toml` (new)

Mirror the reference, minus runtime deps (the project ships a stdlib script):

- `[project]`: `name = "planning-convention"`, `requires-python = ">=3.10,<4"`,
  no runtime `dependencies`.
- `[dependency-groups]`: `dev = ["pytest", "pytest-cov"]`,
  `lint = ["ruff", "ty", "eof-fixer"]`.
- `[tool.ruff]`: `line-length = 120`, `target-version = "py310"`, `fix = true`,
  same ignore set as the reference; `tests/*` → ignore `S101`.
- `[tool.pytest.ini_options]`: `addopts = "--cov=. --cov-report term-missing
  --cov-fail-under=100"`.
- `[tool.coverage.*]`: as in the reference (`exclude_also` for
  `if typing.TYPE_CHECKING:`).

### `Justfile` (new)

```
default: install lint test

install:
    uv sync --all-extras --all-groups --frozen

lint:
    uv run eof-fixer .
    uv run ruff format .
    uv run ruff check . --fix
    uv run ty check

test *args:
    uv run pytest {{ args }}

index:
    uv run python index.py

check-planning:
    uv run python index.py --check
```

`index` / `check-planning` are included because `APPLY.md` says the canonical
repo should model the recipes it tells consumers to install.

## 4. CI rewire

Replace `.github/workflows/check.yml` (inline smoke tests) with a workflow
mirroring the reference `main.yml`, no Postgres service:

- `lint` job: `setup-uv`, `uv python install 3.10`,
  `uv sync --all-extras --all-groups --frozen`, `ruff format --check`,
  `ruff check --no-fix`, `ty check`.
- `pytest` job: `setup-uv`, `uv python install 3.10`, `uv sync ...`,
  `uv run pytest`.

The real suite subsumes the old fixture/template smoke checks.

## 5. Version bump (final step)

- Add a `CHANGELOG.md` `## 1.1.1 — 2026-06-27` entry: internal — `index.py` now
  accepts an explicit `root` (and `main` an `argv`) for testability, with no
  behavior change; the canonical repo gains a `pytest` suite, `pyproject.toml`,
  and `Justfile`.
- Create the `1.1.1` git tag as the last action (after merge, per the user's
  PR-based finish flow).

## Out of scope

- No change to the convention prose (`convention.md`), templates, or `APPLY.md`
  semantics.
- No new runtime dependencies for `index.py`.
- No refactor of `index.py` beyond what testability requires.
