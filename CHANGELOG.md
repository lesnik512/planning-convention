# Changelog

Versions are git tags. A consuming repo records the version it last applied in
`planning/.convention-version`; on update, apply every entry newer than that.

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
