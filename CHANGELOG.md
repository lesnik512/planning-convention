# Changelog

Versions are git tags. A consuming repo records the version it last applied in
`planning/.convention-version`; on update, apply every entry newer than that.

## 1.1.1 — 2026-06-27

Internal: `index.py` now accepts an explicit `root` path
(`load_bundles`/`load_decisions`/`check`) and `main(argv=None, root=None)`, for
testability — no behavior change (identical stdout, violation strings, and exit
codes). The canonical repo gains a `pytest` suite at 100% coverage, a
`pyproject.toml` (uv/ruff/ty), and a `Justfile`. No consumer-facing change
beyond the verbatim `index.py` copy.

## 1.1.0 — 2026-06-26

Adds the **glossary** artifact to the `architecture/` axis:

- **`architecture/glossary.md`**: a single ubiquitous-language page beside the
  capability files — living prose, no frontmatter, authored lazily. Defines the
  domain terms (term · definition · `_Avoid_:`) that code, specs, and capability
  pages share; promoted in the same PR that introduces or sharpens a term.
- **`_templates/glossary.md`**: starting point for the page; lands in consumers
  via the §1 verbatim template copy.
- No validator change — `index.py` covers `planning/`, not `architecture/`.

## 1.0.0 — 2026-06-25

Initial extraction of the convention into this canonical repo. Baseline:

- **Validator + index** (`index.py`): `--check` validates bundle/decision name
  format, bundle shape, and required frontmatter; default mode prints the change
  index as a flat newest-first list. Wired into `just lint-ci` in consumers.
- **Lean frontmatter**: `date` and `slug` are derived from the directory / file
  name, never written in frontmatter. Specs (`design.md`/`change.md`) carry
  `summary` only; plans carry **none**; decisions keep `status`
  (accepted|superseded), `summary`, and optional `supersedes`/`superseded_by`.
  No `pr`, `status`, `outcome`, or `spec` on change bundles.
- **Quick-path on-ramp** with a first-match lane decision; full Conventions
  reference; `_templates/` for change/design/plan/decision/release.
- **architecture/ promotion**: a behavior change updates the matching
  `architecture/<capability>.md` in the same PR; consumers carry an agent-facing
  reminder in `CLAUDE.md`'s `## Architecture` note.
