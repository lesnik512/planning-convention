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


def test_main_check_stderr_format_is_exact(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_bundle(tmp_path, "bad-name", design=VALID_SPEC)

    code = index.main(["--check"], root=tmp_path)

    err = capsys.readouterr().err
    assert code == 1
    assert err == (
        "planning: 1 violation(s)\n"
        "  - changes/bad-name: directory name is not 'YYYY-MM-DD.NN-slug'\n"
    )


def test_dunder_main_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["index.py"])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(INDEX_PATH), run_name="__main__")
    assert excinfo.value.code == 0
