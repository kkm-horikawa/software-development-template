from pathlib import Path

import pytest

from tests.acceptance.sc_001.cases import BackendState, CLIStartCases

CASE_FILE = Path(__file__).parent / "acceptance/sc_001/task.csv"


class TestCLIStartCases:
    def test_load_preserves_input_and_expected_results(self) -> None:
        cases = CLIStartCases(CASE_FILE).load()

        assert [case.case_id for case in cases] == [
            "EX-SC001-02",
            "EX-SC001-04",
            "EX-SC001-05",
        ]
        assert cases[0].backend_state is BackendState.RUNNING
        assert cases[0].stdout() == "開始: 設計を書く\n"
        assert cases[0].expected_success is True
        assert cases[1].title == "   "
        assert cases[1].expected_success is False

    @pytest.mark.parametrize(
        "change",
        [
            "added_column",
            "missing_column",
            "extra_cell",
            "missing_cell",
            "unknown_state",
            "invalid_success",
            "empty",
            "duplicate_id",
            "missing_error",
            "missing_output",
        ],
    )
    def test_rejects_invalid_csv(self, tmp_path: Path, change: str) -> None:
        lines = CASE_FILE.read_text(encoding="utf-8").splitlines()
        match change:
            case "added_column":
                lines[0] += ",started_at"
            case "missing_column":
                lines[0] = lines[0].replace("title,", "", 1)
            case "extra_cell":
                lines[1] += ",extra"
            case "missing_cell":
                lines[1] = lines[1].rsplit(",", 1)[0]
            case "unknown_state":
                lines[1] = lines[1].replace(",running,", ",unknown,")
            case "invalid_success":
                lines[1] = lines[1].replace(",true", ",yes")
            case "empty":
                lines = lines[:1]
            case "duplicate_id":
                lines.append(lines[1])
            case "missing_error":
                lines[2] = lines[2].replace("作業名を空にはできません", "")
            case "missing_output":
                lines[1] = lines[1].replace("開始: 設計を書く", "")
        path = tmp_path / "task.csv"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        with pytest.raises(ValueError, match="task.csv"):
            CLIStartCases(path).load()
