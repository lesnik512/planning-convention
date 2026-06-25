# APPLY.md — adopt or update this planning convention in a repo

You are an agent applying this canonical planning convention to a **target
repo** (the repo you are working in). The canonical repo is
`lesnik512/planning-convention`. Work on a feature branch in the target repo and
open a PR at the end.

## 0. Read the target's baseline

Read `planning/.convention-version` in the target repo.
- **Missing** → FRESH ADOPT: do every section below, including §5.
- **Present** (e.g. `1.0.0`) → UPDATE: read this repo's `CHANGELOG.md` and apply
  only entries with a version GREATER than the recorded one; skip §5.

## 1. Overwrite the clean files verbatim

Owned by the canonical repo — copy exactly, replacing any local version (local
edits to them are intentionally discarded):

- `index.py` → target `planning/index.py`
- `_templates/*` → target `planning/_templates/*`

## 2. Merge the convention prose

`convention.md` here is the portable Quick-path + Conventions prose. In the
target's `planning/README.md`, replace the existing block (from the `## Quick
path` heading through the end of the `## Conventions`/Frontmatter section) with
`convention.md`'s body **below its `# Planning convention` title** (the target
keeps its own page title/intro). Keep the target's repo-local sections (its
`## Index`, `## Other`). Ensure the target README still points at
`planning/.convention-version` and this canonical repo.

## 3. Judgment-merge the mixed files

Edit in place, don't overwrite:

- **`Justfile`**: ensure these recipes exist and match —
  ```
  index:
      uv run python planning/index.py
  check-planning:
      uv run python planning/index.py --check
  ```
  and ensure `lint-ci` runs `uv run python planning/index.py --check` as a step.
  (If the repo uses another task runner, adapt and note the deviation in the PR.)
- **`CLAUDE.md`**: ensure (a) a `## Workflow` pointer to the Quick path in
  `planning/README.md` as the authoritative convention, and (b) the
  `## Architecture` orientation carries the promotion reminder: "When a change
  alters a capability's behavior, update the matching
  `architecture/<capability>.md` in the same PR." Preserve all other
  repo-specific content.

## 4. Apply CHANGELOG deltas (UPDATE only)

For each CHANGELOG entry newer than the recorded version, make the change it
describes if §§1–3 did not already cover it (most land via the §1 verbatim copy).

## 5. Fresh-adopt scaffolding (FRESH ADOPT only)

Create if absent: `planning/{changes,decisions,releases}/`, `planning/deferred.md`
(one-line header), and `architecture/README.md` stating the promotion rule (one
file per capability; shipping a change hand-edits the matching file in the same
PR). The repo authors its own capability files.

## 6. Record, verify, open a PR

- Write the applied version (the latest CHANGELOG version) to
  `planning/.convention-version`.
- `just check-planning` → must print `planning: OK`.
- `just lint-ci` → must pass.
- Commit and open a PR whose body lists the applied CHANGELOG deltas (or "fresh
  adopt at vX.Y.Z"), so the human reviews exactly what changed.
