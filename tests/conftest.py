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
