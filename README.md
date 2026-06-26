# planning-convention

Canonical source for a portable, agent-friendly planning convention: a two-axis
model (`architecture/` truth home + `planning/changes/` bundles), a
`check-planning` validator, lean frontmatter, and a Quick-path on-ramp.

Source: <https://github.com/lesnik512/planning-convention>

## What's here

- [`convention.md`](convention.md) — the portable convention prose (Quick path +
  Conventions).
- [`index.py`](index.py) — the validator + index generator.
- [`_templates/`](_templates/) — change · design · plan · decision · release ·
  glossary.
- [`APPLY.md`](APPLY.md) — how an agent applies/updates this into a repo.
- [`CHANGELOG.md`](CHANGELOG.md) — versioned deltas (git tags are the versions).

## Adopt or update it in a repo

Point an agent (e.g. Claude Code) at [`APPLY.md`](APPLY.md) from the target repo:
it copies the script + templates, merges the convention prose and the
`Justfile`/`CLAUDE.md` snippets, records the applied version in
`planning/.convention-version`, verifies with `just check-planning`, and opens a
PR. Updating re-runs the same flow, applying only the CHANGELOG entries newer
than the recorded version.
