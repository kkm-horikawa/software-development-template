from pathlib import Path

import pytest
from acceptance.sc_001.cases import HTTPStartCases

CASE_FILE = Path(__file__).parent / "acceptance/sc_001/task.csv"


class TestHTTPStartCases:
    def test_load_preserves_input_spaces_and_typed_status(self) -> None:
        cases = HTTPStartCases(CASE_FILE).load()

        assert [case.case_id for case in cases] == ["EX-SC001-01", "EX-SC001-03"]
        assert cases[0].title == "  設計を書く  "
        assert cases[0].status_code == 201
        assert cases[1].response() == {"detail": "作業名を空にはできません"}

    @pytest.mark.parametrize(
        "change",
        [
            "added_column",
            "missing_column",
            "duplicate_column",
            "short_row",
            "long_row",
            "invalid_status",
            "missing_result",
            "empty",
            "duplicate_id",
        ],
    )
    def test_rejects_invalid_csv(self, tmp_path: Path, change: str) -> None:
        original = CASE_FILE.read_text(encoding="utf-8")
        lines = original.splitlines()
        match change:
            case "added_column":
                lines[0] += ",started_at"
            case "missing_column":
                lines[0] = lines[0].replace("title,", "", 1)
            case "duplicate_column":
                lines[0] = lines[0].replace("status_code", "title")
            case "short_row":
                lines[1] = lines[1].rsplit(",", 1)[0]
            case "long_row":
                lines[1] += ",extra"
            case "invalid_status":
                lines[1] = lines[1].replace(",201,", ",invalid,")
            case "missing_result":
                lines[1] = lines[1].replace("11111111-1111-1111-1111-111111111111", "")
            case "empty":
                lines = lines[:1]
            case "duplicate_id":
                lines.append(lines[1])
        path = tmp_path / "task.csv"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        with pytest.raises(ValueError, match="task.csv"):
            HTTPStartCases(path).load()
