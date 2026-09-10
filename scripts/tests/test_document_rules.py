from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]


def load_script(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        name.removesuffix(".py"), ROOT / "scripts" / name
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"検査を読み込めません: {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestDocumentRules:
    def test_document_checks_accept_current_view(self) -> None:
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

    def test_historical_increment_does_not_require_current_test(
        self, tmp_path: Path
    ) -> None:
        directory = tmp_path / "docs/210_increments"
        directory.mkdir(parents=True)
        (directory / "INC-42.md").write_text(
            "対応Issue: #42\n当時の確認: `removed.py::test_old`\n[旧資料](removed.md)\n",
            encoding="utf-8",
        )
        checker = load_script("check-trace.py").TraceCheck(tmp_path)
        assert checker.check_increment_numbers() == []
        entries, failures = checker.read_entries()
        assert entries == {}
        assert failures == []
        assert checker.check_targets(entries, set()) == []

    def test_increment_requires_matching_issue(self, tmp_path: Path) -> None:
        directory = tmp_path / "docs/210_increments"
        directory.mkdir(parents=True)
        (directory / "INC-42.md").write_text("対応Issue: #41\n", encoding="utf-8")
        assert (
            load_script("check-trace.py").TraceCheck(tmp_path).check_increment_numbers()
        )

    def test_missing_class_or_case_is_rejected(self) -> None:
        checker = load_script("check-trace.py").TraceCheck()
        actual = "tests/test_example.py::TestExample::test_run[EX-SC001-01]"
        assert checker.check_targets({"EX-SC001-01": actual}, {actual}) == []
        assert checker.check_targets(
            {"EX-SC001-01": "tests/test_example.py::test_run"}, {actual}
        )
        assert checker.check_targets({"EX-SC001-02": actual}, {actual})

    def test_removed_case_is_rejected(self) -> None:
        checker = load_script("check-trace.py").TraceCheck()
        assert checker.check_targets(
            {
                "EX-SC001-01": "tests/test_example.py::TestExample::test_run[EX-SC001-01]"
            },
            set(),
        )

    def test_added_case_needs_index_entry(self) -> None:
        checker = load_script("check-trace.py").TraceCheck()
        assert checker.check_targets(
            {}, {"tests/test_example.py::TestExample::test_run[EX-SC001-09]"}
        )

    def test_manual_reference_requires_heading(self, tmp_path: Path) -> None:
        directory = tmp_path / "tests/acceptance/manual"
        directory.mkdir(parents=True)
        path = directory / "SC-001.md"
        path.write_text("## EX-SC001-01\n操作と期待結果\n", encoding="utf-8")
        checker = load_script("check-trace.py").TraceCheck(tmp_path)
        entries = {"EX-SC001-01": "tests/acceptance/manual/SC-001.md::EX-SC001-01"}
        assert checker.check_targets(entries, set()) == []
        path.write_text("EX-SC001-01という名前の言及だけ\n", encoding="utf-8")
        assert checker.check_targets(entries, set())
