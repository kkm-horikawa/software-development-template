from pathlib import Path

import pytest

from tests.acceptance.sc_001.cases import BackendState, CLIStartCases


class TestCLIStartCases:
    def test_load_preserves_input_and_expected_results(self, tmp_path: Path) -> None:
        cases = CLIStartCases(self.sample_csv(tmp_path)).load()

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
        lines = self.sample_csv(tmp_path).read_text(encoding="utf-8").splitlines()
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

    def sample_csv(self, tmp_path: Path) -> Path:
        path = tmp_path / "task.csv"
        path.write_text(
            "case_id,backend_state,title,expected_stdout_line,expected_error,expected_success\n"
            "EX-SC001-02,running,設計を書く,開始: 設計を書く,,true\n"
            'EX-SC001-04,unreachable,"   ",,作業名を空にはできません,false\n'
            "EX-SC001-05,unreachable,設計を書く,,バックエンドへ作業開始を依頼できません,false\n",
            encoding="utf-8",
        )
        return path

    def test_accepts_added_and_reordered_rows(self, tmp_path: Path) -> None:
        path = self.sample_csv(tmp_path)
        lines = path.read_text(encoding="utf-8").splitlines()
        added = lines[1].replace("EX-SC001-02", "new-case")
        path.write_text(
            "\n".join([lines[0], added, *reversed(lines[1:])]) + "\n", encoding="utf-8"
        )

        cases = CLIStartCases(path).load()

        assert cases[0].case_id == "new-case"
        assert len(cases) == 4
