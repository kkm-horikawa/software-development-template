from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_script(name: str) -> ModuleType:
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"検査を読み込めません: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_document_checks_accept_the_template_current_view() -> None:
    for script, expected in (
        ("check-docs.py", "文書の構造: OK"),
        ("check-trace.py", "要求から受入例とテストの対応: OK"),
    ):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        assert result.stdout.strip() == expected


def test_trace_rejects_an_id_from_another_issue(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    check_trace = load_script("check-trace.py")
    increment = tmp_path / "INC-42.md"
    increment.write_text("対応Issue: #42\n", encoding="utf-8")
    monkeypatch.setattr(check_trace, "ROOT", tmp_path)
    monkeypatch.setattr(check_trace, "increment_documents", lambda: [increment])
    found = {"ST-41-01": (increment, 1, set())}

    failures = check_trace.validate_increment_numbers(found)

    assert any("増分キー" in failure for failure in failures)


def test_trace_accepts_a_manual_example_reference() -> None:
    check_trace = load_script("check-trace.py")

    reference = check_trace.TEST_REFERENCE.fullmatch(
        "`tests/acceptance/manual/SC-001.md::EX-SC001-06`"
    )

    assert reference is not None
    assert reference.group(1) == "tests/acceptance/manual/SC-001.md::EX-SC001-06"


def test_trace_rejects_a_missing_test_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    check_trace = load_script("check-trace.py")
    test_file = tmp_path / "tests/acceptance/sc_001/test_example.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def another_test():\n    pass\n", encoding="utf-8")
    requirement = tmp_path / "受入例.md"
    monkeypatch.setattr(check_trace, "ROOT", tmp_path)
    monkeypatch.setattr(
        check_trace,
        "section_test_references",
        lambda: {
            "EX-SC001-01": ["tests/acceptance/sc_001/test_example.py::test_sc001_ex01"]
        },
    )
    found = {"EX-SC001-01": (requirement, 1, set())}

    failures = check_trace.validate_test_references(found)

    assert any("存在しないテスト名" in failure for failure in failures)
