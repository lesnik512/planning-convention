# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is the **canonical source** of a portable planning convention — not an
application that consumes it. The files here are *published artifacts* that other
("consuming"/"target") repos copy in via the `APPLY.md` flow. Keep the
distinction in mind: edits here change what every downstream repo will adopt on
its next update.

Five top-level artifacts, each with a distinct owner/role:

- `convention.md` — the portable convention **prose** (Quick path + Conventions).
  This is the human-facing spec. In a consuming repo its body is merged into
  `planning/README.md`.
- `index.py` — the **validator + index generator** (the only code). Lands in
  consumers at `planning/index.py`.
- `_templates/*` — starting points for each artifact (change · design · plan ·
  decision · release · glossary). Copied **verbatim** into consumers.
- `APPLY.md` — the **agent runbook** for adopting/updating the convention into a
  target repo. Read this to understand how the pieces propagate.
- `CHANGELOG.md` — versioned deltas. **Git tags are the versions.** A consumer
  records the version it last applied in `planning/.convention-version`; on
  update it applies every CHANGELOG entry newer than that.

## Commands

```bash
python3 index.py --check   # validate bundles/decisions; prints "planning: OK" or violations (exit 1)
python3 index.py           # print the Markdown change index to stdout (never writes a file)
```

There is **no Justfile in this repo** — the `just index` / `just check-planning`
recipes referenced throughout the prose are what `APPLY.md` installs into
*consuming* repos. Here, invoke `index.py` directly. CI
(`.github/workflows/check.yml`) runs `index.py --check` against a generated
fixture and asserts every template (except `release.md`, `plan.md`,
`glossary.md`, which carry no frontmatter) parses as frontmatter.

`index.py` resolves `changes/` and `decisions/` relative to its own parent
directory and tolerates their absence — so it runs clean here at the repo root
even though this repo has no `planning/` tree of its own.

## The convention being published (the mental model)

Understanding `convention.md` is required before editing any artifact, because
the prose, the templates, and the validator must agree.

- **Two axes, never mixed.** `architecture/` (repo root, in a consumer) holds
  living truth about what the system does *now* — one file per capability plus a
  single `glossary.md`, no frontmatter, dated by git. `planning/changes/` holds
  the past-and-pending — one folder per change, kept in place after ship. A
  change **promotes** its conclusions into the affected
  `architecture/<capability>.md` by hand, in the same PR as the code.
- **Three lanes** (first matching rule wins): **Full** (`design.md` + `plan.md`),
  **Lightweight** (`change.md`), **Tiny** (no bundle, conventional commit).
- **Lean frontmatter** is the load-bearing invariant the validator enforces:
  `date` and `slug` are **derived from the directory/file name, never written**.
  Specs (`design.md`/`change.md`) carry `summary` only; `plan.md` carries none;
  `decisions/*.md` carry `status` (accepted|superseded) + `summary` (+ optional
  `supersedes`/`superseded_by`); `architecture/` files carry none.

`index.py` encodes these rules concretely: `BUNDLE_RE`
(`YYYY-MM-DD.NN-slug`), `DECISION_RE` (`YYYY-MM-DD-slug`), `ALLOWED_BUNDLE_FILES`,
`SPEC_REQUIRED`, `DECISION_REQUIRED`, `VALID_DECISION_STATUS`.

## When making changes here

These artifacts are coupled — a change to one usually forces matching edits to
others, and to the propagation path:

- Changing the convention rules → update `convention.md` (prose), the relevant
  `_templates/*`, **and** `index.py` if the rule is machine-checkable (frontmatter
  keys, name format, allowed files). The three must not drift.
- Any user-visible change → add a `CHANGELOG.md` entry with the **next semver**
  and bump the version, and confirm `APPLY.md`'s §§1–5 still describe how a
  consumer should pick it up. New owned files must be listed in `APPLY.md` §1
  (verbatim copy) or §5 (fresh-adopt scaffolding).
- `parse_frontmatter` is deliberately a minimal single-line-scalar YAML reader,
  not a real YAML parser — keep templates within what it parses (CI asserts this).
- Run `python3 index.py --check` before declaring done.
