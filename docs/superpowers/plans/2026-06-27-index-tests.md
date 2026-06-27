# index.py Test Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give `index.py` a 100%-coverage pytest suite, refactoring it for testability, with full template-aligned tooling and CI.

**Architecture:** Refactor `index.py` to thread an explicit `root: pathlib.Path` (replacing `__file__`-derived module constants) and make `main(argv=None, root=None)`, preserving behavior exactly. Add a `uv`-managed `pytest`/`ruff`/`ty` toolchain, a fixture-driven test suite under `tests/`, and a CI workflow mirroring the `fastapi-sqlalchemy-template` reference. Bump the convention to `1.1.1`.

**Tech Stack:** Python ≥3.10 (stdlib-only runtime), `uv`, `pytest`, `pytest-cov`, `ruff`, `ty`, `eof-fixer`, GitHub Actions.

## Global Constraints

- `requires-python = ">=3.10,<4"`; ruff `target-version = "py310"`.
- `index.py` has **no runtime dependencies** (stdlib only); new deps are test/lint-time only.
- **Behavior invariant:** the `index.py` refactor must preserve identical stdout, identical violation strings, and identical exit codes. Asserted by a snapshot test.
- Coverage gate: `--cov-fail-under=100`. Intermediate per-file test runs use `--no-cov`; the final task verifies the full 100% gate.
- Test code: annotate **all** function args and return types (`-> None`); `assert` is allowed (`S101` ignored for `tests/*`); docstrings not required (`D1` ignored).
- Keep `index.py`'s existing `# ruff: noqa: INP001, D212` header line verbatim.
- Commits: conventional-commit style; do not mention Claude Code in messages.

---

### Task 1: Repo tooling scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `Justfile`

**Interfaces:**
- Consumes: nothing.
- Produces: a working `uv` environment with `pytest`/`ruff`/`ty`; `just` recipes `install`, `lint`, `test`, `index`, `check-planning`.

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "planning-convention"
version = "0"
description = "Portable, agent-friendly planning convention: validator + index generator"
readme = "README.md"
requires-python = ">=3.10,<4"
authors = [
    { name = "Artur Shiriev", email = "me@shiriev.ru" },
]
license = "MIT License"
dependencies = []

[dependency-groups]
dev = [
    "pytest",
    "pytest-cov",
]
lint = [
    "ruff",
    "ty",
    "eof-fixer",
]

[tool.ruff]
fix = true
unsafe-fixes = true
line-length = 120
target-version = "py310"

[tool.ruff.lint]
select = ["ALL"]
ignore = [
    "D1", # allow missing docstrings
    "FBT", # allow boolean args
    "INP", # ignore flake8-no-pep420
    "B008", # function-call-in-default-argument
    "ANN204", # no typings for __init__
    "RUF001", # allow cyrillic letters
    "D203", # "one-blank-line-before-class" conflicting with D211
    "D213", # "multi-line-summary-second-line" conflicting with D212
    "COM812", # flake8-commas "Trailing comma missing"
    "ISC001", # flake8-implicit-str-concat
    "S105", # Possible hardcoded password
]
isort.lines-after-imports = 2
isort.no-lines-before = ["standard-library", "local-folder"]

[tool.ruff.lint.extend-per-file-ignores]
"tests/*.py" = [
    "S101", # allow asserts
    "PLR2004", # allow magic-value comparisons (exit codes 0/1) in assertions
]

[tool.pytest.ini_options]
addopts = "--cov=. --cov-report term-missing --cov-fail-under=100"

[tool.coverage.report]
exclude_also = [
    "if typing.TYPE_CHECKING:",
]
```

- [ ] **Step 2: Create `Justfile`**

```just
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

- [ ] **Step 3: Sync the environment**

Run: `uv sync --all-extras --all-groups`
Expected: resolves and creates `.venv` with pytest/ruff/ty; writes `uv.lock`. (`uv.lock` is git-ignored per the user's convention — do not commit it.)

- [ ] **Step 4: Sanity-check the toolchain against the unchanged script**

Run: `uv run python index.py`
Expected: prints the "# Planning index" markdown with empty `## Changes` / `## Decisions` sections (this repo has no `changes/`/`decisions/` dirs), exit 0.

Run: `uv run ruff check .`
Expected: passes (the existing `index.py` already conforms; if ruff reports issues, fix them minimally without altering behavior).

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml Justfile .gitignore
git commit -m "chore: add uv/pytest/ruff/ty tooling"
```

(If `uv.lock` is not already ignored, add `uv.lock` to `.gitignore` in this step.)

---

### Task 2: Refactor index.py for testability + main/CLI tests

**Files:**
- Modify: `index.py` (constants block, `load_bundles`, `load_decisions`, `check`, `main`)
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_main.py`

**Interfaces:**
- Consumes: `index` module.
- Produces:
  - `index.ROOT: pathlib.Path` (module default root)
  - `index.load_bundles(root: pathlib.Path) -> list[dict[str, str]]`
  - `index.load_decisions(root: pathlib.Path) -> list[dict[str, str]]`
  - `index.check(root: pathlib.Path) -> list[str]`
  - `index.main(argv: list[str] | None = None, root: pathlib.Path | None = None) -> int`
  - `tests/conftest.py` helpers: `write_bundle(root, name, *, design=None, change=None, plan=None, extra=None) -> pathlib.Path` and `write_decision(root, name, content) -> pathlib.Path`, plus `VALID_SPEC` / `VALID_DECISION` content constants.

- [ ] **Step 1: Create `tests/__init__.py`**

Empty file:

```python
```

- [ ] **Step 2: Create `tests/conftest.py` with fixture helpers**

```python
import pathlib


VALID_SPEC = "---\nsummary: did a thing\n---\n# body\n"
VALID_DECISION = "---\nstatus: accepted\nsummary: chose X over Y\n---\n# body\n"


def write_bundle(
    root: pathlib.Path,
    name: str,
    *,
    design: str | None = None,
    change: str | None = None,
    plan: str | None = None,
    extra: dict[str, str] | None = None,
) -> pathlib.Path:
    """Create a change bundle dir under ``root/changes/<name>`` and return it."""
    bundle = root / "changes" / name
    bundle.mkdir(parents=True)
    if design is not None:
        (bundle / "design.md").write_text(design, encoding="utf-8")
    if change is not None:
        (bundle / "change.md").write_text(change, encoding="utf-8")
    if plan is not None:
        (bundle / "plan.md").write_text(plan, encoding="utf-8")
    for filename, content in (extra or {}).items():
        (bundle / filename).write_text(content, encoding="utf-8")
    return bundle


def write_decision(root: pathlib.Path, name: str, content: str) -> pathlib.Path:
    """Create a decision file under ``root/decisions/<name>`` and return it."""
    decisions = root / "decisions"
    decisions.mkdir(parents=True, exist_ok=True)
    path = decisions / name
    path.write_text(content, encoding="utf-8")
    return path
```

- [ ] **Step 3: Write the failing test `tests/test_main.py`**

```python
import pathlib
import runpy
import sys

import pytest

import index
from tests.conftest import VALID_DECISION, VALID_SPEC, write_bundle, write_decision


INDEX_PATH = pathlib.Path(index.__file__)


def test_main_prints_index(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_bundle(tmp_path, "2026-01-02.01-alpha", design=VALID_SPEC)
    write_decision(tmp_path, "2026-01-03-beta.md", VALID_DECISION)

    code = index.main([], root=tmp_path)

    out = capsys.readouterr().out
    assert code == 0
    assert "# Planning index" in out
    assert "alpha" in out
    assert "beta" in out


def test_main_check_ok(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_bundle(tmp_path, "2026-01-02.01-alpha", design=VALID_SPEC)

    code = index.main(["--check"], root=tmp_path)

    assert code == 0
    assert capsys.readouterr().out == "planning: OK\n"


def test_main_check_reports_violations(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_bundle(tmp_path, "bad-name", design="---\nsummary: x\n---\n")

    code = index.main(["--check"], root=tmp_path)

    err = capsys.readouterr().err
    assert code == 1
    assert "planning: 1 violation(s)" in err
    assert "directory name is not" in err


def test_main_defaults_to_repo_root_no_dirs(capsys: pytest.CaptureFixture[str]) -> None:
    # The repo root has no changes/decisions dirs: renders empty sections, exit 0.
    code = index.main([])

    out = capsys.readouterr().out
    assert code == 0
    assert "_None._" in out


def test_dunder_main_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["index.py"])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(INDEX_PATH), run_name="__main__")
    assert excinfo.value.code == 0
```

- [ ] **Step 4: Run the test to verify it fails**

Run: `uv run pytest tests/test_main.py -v --no-cov`
Expected: FAIL — `index.main()` does not accept `root=`/positional `argv` yet (TypeError), and `index.load_bundles`/`check` take no args.

- [ ] **Step 5: Refactor `index.py`**

Replace the constants block (current lines 20–21):

```python
ROOT = pathlib.Path(__file__).parent
```

(Delete `CHANGES_DIR` and `DECISIONS_DIR`; keep `VALID_DECISION_STATUS`, `BUNDLE_RE`, `DECISION_RE`, `ALLOWED_BUNDLE_FILES`, `SPEC_REQUIRED`, `DECISION_REQUIRED` unchanged.)

Replace `load_bundles`:

```python
def load_bundles(root: pathlib.Path) -> list[dict[str, str]]:
    """Read each bundle's summary; derive date/slug from the directory name."""
    changes_dir = root / "changes"
    bundles: list[dict[str, str]] = []
    if not changes_dir.is_dir():
        return bundles
    for bundle in sorted(changes_dir.iterdir()):
        if not bundle.is_dir():
            continue
        spec = bundle / "design.md"
        if not spec.exists():
            spec = bundle / "change.md"
        if not spec.exists():
            continue
        fields = _named(parse_frontmatter(spec.read_text(encoding="utf-8")), bundle.name, BUNDLE_RE)
        fields["path"] = f"changes/{bundle.name}/{spec.name}"
        fields["name"] = bundle.name
        bundles.append(fields)
    return bundles
```

Replace `load_decisions`:

```python
def load_decisions(root: pathlib.Path) -> list[dict[str, str]]:
    """Read each decision's frontmatter; derive date/slug from the file name."""
    decisions_dir = root / "decisions"
    decisions: list[dict[str, str]] = []
    if not decisions_dir.is_dir():
        return decisions
    for path in sorted(decisions_dir.glob("*.md")):
        if path.name == "README.md" or path.name.startswith("_"):
            continue
        fields = _named(parse_frontmatter(path.read_text(encoding="utf-8")), path.stem, DECISION_RE)
        fields["path"] = f"decisions/{path.name}"
        fields["name"] = path.stem
        decisions.append(fields)
    return decisions
```

Replace `check`:

```python
def check(root: pathlib.Path) -> list[str]:
    """Validate every bundle and decision; return the list of violation strings."""
    violations: list[str] = []
    changes_dir = root / "changes"
    decisions_dir = root / "decisions"
    if changes_dir.is_dir():
        for bundle in sorted(changes_dir.iterdir()):
            if bundle.is_dir():
                _check_bundle(bundle, violations)
    if decisions_dir.is_dir():
        for path in sorted(decisions_dir.glob("*.md")):
            if path.name == "README.md" or path.name.startswith("_"):
                continue
            _check_decision(path, violations)
    return violations
```

Replace `main`:

```python
def main(argv: list[str] | None = None, root: pathlib.Path | None = None) -> int:
    """Print the listing to stdout, or validate bundles with --check."""
    argv = sys.argv[1:] if argv is None else argv
    root = ROOT if root is None else root
    if "--check" in argv:
        violations = check(root)
        if violations:
            sys.stderr.write(f"planning: {len(violations)} violation(s)\n")
            for violation in violations:
                sys.stderr.write(f"  - {violation}\n")
            return 1
        sys.stdout.write("planning: OK\n")
        return 0
    sys.stdout.write(render(load_bundles(root), load_decisions(root)))
    return 0
```

(`_named`, `parse_frontmatter`, `format_row`, `render`, `_require`, `_check_spec_file`, `_check_bundle`, `_check_decision`, and the `if __name__ == "__main__": raise SystemExit(main())` guard are unchanged.)

- [ ] **Step 6: Run the test to verify it passes**

Run: `uv run pytest tests/test_main.py -v --no-cov`
Expected: PASS (5 tests).

- [ ] **Step 7: Confirm the CLI still behaves identically**

Run: `uv run python index.py --check`
Expected: `planning: OK` (no `changes/`/`decisions/` dirs at repo root → no violations), exit 0.

- [ ] **Step 8: Commit**

```bash
git add index.py tests/__init__.py tests/conftest.py tests/test_main.py
git commit -m "refactor: thread root through index.py; add main/CLI tests"
```

---

### Task 3: parse_frontmatter tests

**Files:**
- Create: `tests/test_parse_frontmatter.py`

**Interfaces:**
- Consumes: `index.parse_frontmatter(text: str) -> dict[str, str]`.
- Produces: nothing for later tasks.

- [ ] **Step 1: Write the test file**

```python
import index


def test_empty_input_returns_empty() -> None:
    assert index.parse_frontmatter("") == {}


def test_no_leading_delimiter_returns_empty() -> None:
    assert index.parse_frontmatter("# heading\nsummary: x\n") == {}


def test_parses_single_line_scalars() -> None:
    text = "---\nsummary: did a thing\nstatus: accepted\n---\n# body\n"
    assert index.parse_frontmatter(text) == {"summary": "did a thing", "status": "accepted"}


def test_null_value_becomes_empty_string() -> None:
    assert index.parse_frontmatter("---\nsummary: null\n---\n") == {"summary": ""}


def test_quotes_are_stripped() -> None:
    text = "---\na: \"double\"\nb: 'single'\n---\n"
    assert index.parse_frontmatter(text) == {"a": "double", "b": "single"}


def test_line_without_separator_is_skipped() -> None:
    text = "---\nnocolon\nsummary: kept\n---\n"
    assert index.parse_frontmatter(text) == {"summary": "kept"}


def test_indented_continuation_lines_are_skipped() -> None:
    text = "---\nsummary: kept\n  indented: ignored\n\ttabbed: ignored\n---\n"
    assert index.parse_frontmatter(text) == {"summary": "kept"}


def test_second_delimiter_terminates_block() -> None:
    text = "---\nsummary: kept\n---\nafter: ignored\n"
    assert index.parse_frontmatter(text) == {"summary": "kept"}
```

- [ ] **Step 2: Run the tests**

Run: `uv run pytest tests/test_parse_frontmatter.py -v --no-cov`
Expected: PASS (8 tests). `parse_frontmatter` is unchanged from the original, so these characterize existing behavior.

- [ ] **Step 3: Commit**

```bash
git add tests/test_parse_frontmatter.py
git commit -m "test: cover parse_frontmatter"
```

---

### Task 4: load_bundles / load_decisions tests

**Files:**
- Create: `tests/test_load.py`

**Interfaces:**
- Consumes: `index.load_bundles(root)`, `index.load_decisions(root)`, conftest helpers.
- Produces: nothing for later tasks.

- [ ] **Step 1: Write the test file**

```python
import pathlib

import index
from tests.conftest import VALID_DECISION, VALID_SPEC, write_bundle, write_decision


def test_load_bundles_missing_dir_returns_empty(tmp_path: pathlib.Path) -> None:
    assert index.load_bundles(tmp_path) == []


def test_load_bundles_prefers_design_over_change(tmp_path: pathlib.Path) -> None:
    write_bundle(
        tmp_path,
        "2026-01-02.01-alpha",
        design="---\nsummary: from design\n---\n",
        change="---\nsummary: from change\n---\n",
    )

    (row,) = index.load_bundles(tmp_path)

    assert row["summary"] == "from design"
    assert row["path"] == "changes/2026-01-02.01-alpha/design.md"
    assert row["name"] == "2026-01-02.01-alpha"
    assert row["date"] == "2026-01-02"
    assert row["slug"] == "alpha"


def test_load_bundles_falls_back_to_change(tmp_path: pathlib.Path) -> None:
    write_bundle(tmp_path, "2026-01-02.01-alpha", change=VALID_SPEC)

    (row,) = index.load_bundles(tmp_path)

    assert row["path"] == "changes/2026-01-02.01-alpha/change.md"


def test_load_bundles_skips_bundle_without_spec(tmp_path: pathlib.Path) -> None:
    write_bundle(tmp_path, "2026-01-02.01-alpha", plan="# plan only\n")

    assert index.load_bundles(tmp_path) == []


def test_load_bundles_skips_non_directory_entries(tmp_path: pathlib.Path) -> None:
    (tmp_path / "changes").mkdir()
    (tmp_path / "changes" / "stray.md").write_text("not a bundle\n", encoding="utf-8")

    assert index.load_bundles(tmp_path) == []


def test_load_bundles_unmatched_name_has_no_date_slug(tmp_path: pathlib.Path) -> None:
    # Exercises the no-match branch of _named: load_bundles does not validate
    # names, so an unmatched dir is still listed but without date/slug.
    write_bundle(tmp_path, "weird", design=VALID_SPEC)

    (row,) = index.load_bundles(tmp_path)

    assert "date" not in row
    assert "slug" not in row
    assert row["name"] == "weird"


def test_load_decisions_missing_dir_returns_empty(tmp_path: pathlib.Path) -> None:
    assert index.load_decisions(tmp_path) == []


def test_load_decisions_reads_and_derives_name(tmp_path: pathlib.Path) -> None:
    write_decision(tmp_path, "2026-01-03-beta.md", VALID_DECISION)

    (row,) = index.load_decisions(tmp_path)

    assert row["status"] == "accepted"
    assert row["path"] == "decisions/2026-01-03-beta.md"
    assert row["name"] == "2026-01-03-beta"
    assert row["date"] == "2026-01-03"
    assert row["slug"] == "beta"


def test_load_decisions_skips_readme_and_underscore(tmp_path: pathlib.Path) -> None:
    write_decision(tmp_path, "README.md", "# readme\n")
    write_decision(tmp_path, "_draft.md", VALID_DECISION)

    assert index.load_decisions(tmp_path) == []
```

- [ ] **Step 2: Run the tests**

Run: `uv run pytest tests/test_load.py -v --no-cov`
Expected: PASS (9 tests).

- [ ] **Step 3: Commit**

```bash
git add tests/test_load.py
git commit -m "test: cover load_bundles and load_decisions"
```

---

### Task 5: check() violation-branch tests

**Files:**
- Create: `tests/test_check.py`

**Interfaces:**
- Consumes: `index.check(root)`, conftest helpers.
- Produces: nothing for later tasks.

- [ ] **Step 1: Write the test file**

```python
import pathlib

import index
from tests.conftest import VALID_DECISION, VALID_SPEC, write_bundle, write_decision


def test_clean_tree_has_no_violations(tmp_path: pathlib.Path) -> None:
    write_bundle(tmp_path, "2026-01-02.01-alpha", design=VALID_SPEC, plan="# plan\n")
    write_decision(tmp_path, "2026-01-03-beta.md", VALID_DECISION)

    assert index.check(tmp_path) == []


def test_bad_bundle_name(tmp_path: pathlib.Path) -> None:
    write_bundle(tmp_path, "not-a-date", design=VALID_SPEC)

    violations = index.check(tmp_path)

    assert any("directory name is not 'YYYY-MM-DD.NN-slug'" in v for v in violations)


def test_unexpected_file_in_bundle(tmp_path: pathlib.Path) -> None:
    write_bundle(tmp_path, "2026-01-02.01-alpha", design=VALID_SPEC, extra={"notes.md": "x\n"})

    violations = index.check(tmp_path)

    assert any("unexpected file in bundle" in v for v in violations)


def test_bundle_without_spec(tmp_path: pathlib.Path) -> None:
    write_bundle(tmp_path, "2026-01-02.01-alpha", plan="# plan only\n")

    violations = index.check(tmp_path)

    assert any("has neither design.md nor change.md" in v for v in violations)


def test_spec_missing_summary(tmp_path: pathlib.Path) -> None:
    write_bundle(tmp_path, "2026-01-02.01-alpha", design="---\ntitle: x\n---\n")

    violations = index.check(tmp_path)

    assert any("missing or empty frontmatter key 'summary'" in v for v in violations)


def test_bad_decision_name(tmp_path: pathlib.Path) -> None:
    write_decision(tmp_path, "nodate.md", VALID_DECISION)

    violations = index.check(tmp_path)

    assert any("file name is not 'YYYY-MM-DD-slug.md'" in v for v in violations)


def test_decision_missing_required_keys(tmp_path: pathlib.Path) -> None:
    write_decision(tmp_path, "2026-01-03-beta.md", "---\ntitle: x\n---\n")

    violations = index.check(tmp_path)

    assert any("missing or empty frontmatter key 'status'" in v for v in violations)
    assert any("missing or empty frontmatter key 'summary'" in v for v in violations)


def test_decision_invalid_status(tmp_path: pathlib.Path) -> None:
    write_decision(tmp_path, "2026-01-03-beta.md", "---\nstatus: bogus\nsummary: s\n---\n")

    violations = index.check(tmp_path)

    assert any("invalid status 'bogus'" in v for v in violations)


def test_check_skips_readme_and_underscore_decisions(tmp_path: pathlib.Path) -> None:
    # Exercises check()'s own README/_ skip branch (distinct from load_decisions).
    write_decision(tmp_path, "README.md", "# readme\n")
    write_decision(tmp_path, "_draft.md", "---\nnothing: here\n---\n")
    write_decision(tmp_path, "2026-01-03-beta.md", VALID_DECISION)

    assert index.check(tmp_path) == []
```

- [ ] **Step 2: Run the tests**

Run: `uv run pytest tests/test_check.py -v --no-cov`
Expected: PASS (9 tests).

- [ ] **Step 3: Commit**

```bash
git add tests/test_check.py
git commit -m "test: cover check() violation branches"
```

---

### Task 6: format_row / render tests + behavior-invariant snapshot

**Files:**
- Create: `tests/test_render.py`

**Interfaces:**
- Consumes: `index.format_row(bundle)`, `index.render(bundles, decisions)`, `index.load_bundles`, `index.load_decisions`, conftest helpers.
- Produces: nothing for later tasks.

- [ ] **Step 1: Write the test file**

```python
import pathlib

import index
from tests.conftest import VALID_DECISION, VALID_SPEC, write_bundle, write_decision


def test_format_row_minimal() -> None:
    row = {"slug": "alpha", "path": "changes/x/design.md", "date": "2026-01-02", "summary": "did it"}
    assert index.format_row(row) == "- **[alpha](changes/x/design.md)** (2026-01-02) — did it"


def test_format_row_no_summary_fallback() -> None:
    assert "(no summary)" in index.format_row({"slug": "a", "path": "p", "date": "d"})


def test_format_row_supersedes() -> None:
    row = {"slug": "a", "path": "p", "date": "d", "summary": "s", "supersedes": "old"}
    assert index.format_row(row).endswith("_(supersedes old)_")


def test_format_row_superseded_by() -> None:
    row = {"slug": "a", "path": "p", "date": "d", "summary": "s", "superseded_by": "new"}
    assert index.format_row(row).endswith("_(superseded by new)_")


def test_render_empty_sections() -> None:
    out = index.render([], [])
    assert "## Changes\n\n_None._" in out
    assert "## Decisions\n\n_None._" in out


def test_render_orders_newest_first() -> None:
    bundles = [
        {"name": "2026-01-01.01-old", "slug": "old", "path": "p1", "date": "2026-01-01", "summary": "o"},
        {"name": "2026-01-09.01-new", "slug": "new", "path": "p2", "date": "2026-01-09", "summary": "n"},
    ]
    out = index.render(bundles, [])
    assert out.index("new") < out.index("old")


def test_full_render_snapshot(tmp_path: pathlib.Path) -> None:
    write_bundle(tmp_path, "2026-01-02.01-alpha", design="---\nsummary: shipped alpha\n---\n")
    write_decision(tmp_path, "2026-01-03-beta.md", VALID_DECISION)

    out = index.render(index.load_bundles(tmp_path), index.load_decisions(tmp_path))

    assert out == (
        "# Planning index\n"
        "\n"
        "_Generated by `just index` — do not edit._\n"
        "\n"
        "## Changes\n"
        "\n"
        "- **[alpha](changes/2026-01-02.01-alpha/design.md)** (2026-01-02) — shipped alpha\n"
        "\n"
        "## Decisions\n"
        "\n"
        "- **[beta](decisions/2026-01-03-beta.md)** (2026-01-03) — chose X over Y\n"
    )
```

- [ ] **Step 2: Run the tests**

Run: `uv run pytest tests/test_render.py -v --no-cov`
Expected: PASS (7 tests). If the snapshot mismatches, the refactor altered output — STOP and reconcile against the unchanged `render`/`format_row` (behavior invariant), do not edit the expected string to paper over a regression.

- [ ] **Step 3: Commit**

```bash
git add tests/test_render.py
git commit -m "test: cover format_row and render with snapshot"
```

---

### Task 7: Full coverage gate, lint/type pass, CI rewire, version bump

**Files:**
- Delete + Create: `.github/workflows/check.yml`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: everything above.
- Produces: green CI; recorded `1.1.1`.

- [ ] **Step 1: Run the full suite with the 100% coverage gate**

Run: `uv run pytest`
Expected: PASS with `Required test coverage of 100% reached`. If any line of `index.py`/`tests/*` is missing, the term-missing report names it — add the covering test to the appropriate `tests/test_*.py` before continuing.

- [ ] **Step 2: Run lint and type checks**

Run: `uv run ruff format --check . && uv run ruff check . --no-fix && uv run ty check`
Expected: all pass. Fix any findings (formatting, lint, types) without changing runtime behavior, then re-run.

- [ ] **Step 3: Replace the CI workflow**

Overwrite `.github/workflows/check.yml` with:

```yaml
name: CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

concurrency:
  group: ${{ github.head_ref || github.run_id }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/setup-uv@v8.2.0
      - run: uv python install 3.10
      - run: |
          uv sync --all-extras --all-groups
          uv run ruff format . --check
          uv run ruff check . --no-fix
          uv run ty check

  pytest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/setup-uv@v8.2.0
      - run: uv python install 3.10
      - run: |
          uv sync --all-extras --all-groups
          uv run pytest
```

- [ ] **Step 4: Add the CHANGELOG entry**

Insert directly below the `Versions are git tags...` paragraph, above `## 1.1.0 — 2026-06-26`:

```markdown
## 1.1.1 — 2026-06-27

Internal: `index.py` now accepts an explicit `root` path
(`load_bundles`/`load_decisions`/`check`) and `main(argv=None, root=None)`, for
testability — no behavior change (identical stdout, violation strings, and exit
codes). The canonical repo gains a `pytest` suite at 100% coverage, a
`pyproject.toml` (uv/ruff/ty), and a `Justfile`. No consumer-facing change
beyond the verbatim `index.py` copy.
```

- [ ] **Step 5: Final verification before commit**

Run: `uv run pytest && uv run ruff check . --no-fix && uv run ty check`
Expected: tests at 100%, lint clean, types clean.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/check.yml CHANGELOG.md
git commit -m "ci: run pytest/ruff/ty; changelog 1.1.1"
```

- [ ] **Step 7: Push and open the PR**

```bash
git push -u origin tests-for-index
gh pr create --fill
```

Then watch CI: `gh pr checks --watch`. The `1.1.1` git tag is created **after merge** (per the user's PR-based finish flow), not in this branch.

---

## Notes for the executor

- Run intermediate per-file tests with `--no-cov` to avoid the `--cov-fail-under=100` gate failing mid-build; the gate is verified once, in Task 7 Step 1.
- `uv.lock` is git-ignored — never add it to a commit.
- If `ruff check .` flags the refactored `index.py` (e.g. `PLR`/`SIM` on `main`), prefer a minimal, behavior-preserving fix; if a rule genuinely conflicts with the design, surface it rather than silently restructuring.
- The behavior-invariant snapshot (Task 6) is the guard rail: never edit its expected output to make a failing test pass — investigate the refactor instead.
