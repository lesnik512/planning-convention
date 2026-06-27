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
