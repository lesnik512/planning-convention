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
