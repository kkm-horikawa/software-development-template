import csv
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class BackendState(Enum):
    RUNNING = "running"
    UNREACHABLE = "unreachable"
    INVALID_RESPONSE = "invalid_response"
    LOST_RESPONSE = "lost_response"
    STORAGE_FAILURE = "storage_failure"


@dataclass(frozen=True)
class CLIStartCase:
    case_id: str
    backend_state: BackendState
    title: str
    expected_stdout_line: str
    expected_error: str
    expected_success: bool

    def stdout(self) -> str:
        return self.expected_stdout_line + "\n" if self.expected_stdout_line else ""


class CLIStartCases:
    COLUMNS = (
        "case_id",
        "backend_state",
        "title",
        "expected_stdout_line",
        "expected_error",
        "expected_success",
    )

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> list[CLIStartCase]:
        with self.path.open(encoding="utf-8", newline="") as source:
            reader = csv.reader(source, strict=True)
            self.validate_header(next(reader, []))
            cases = [self.read_case(row, reader.line_num) for row in reader]
        self.validate_cases(cases)
        return cases

    def validate_header(self, header: list[str]) -> None:
        if tuple(header) != self.COLUMNS:
            raise ValueError(f"{self.path.name}: CSVの列が想定と一致しません: {header}")

    def read_case(self, row: list[str], line: int) -> CLIStartCase:
        if len(row) != len(self.COLUMNS):
            raise ValueError(f"{self.path.name}:{line}: CSVの列数が一致しません")
        case_id, state, title, stdout, error, success = row
        if state not in {member.value for member in BackendState}:
            raise ValueError(f"{self.path.name}:{line}: 未対応の接続先状態: {state}")
        if success not in {"true", "false"}:
            raise ValueError(f"{self.path.name}:{line}: 成功判定はtrueまたはfalseです")
        if success == "true" and (not stdout or error):
            raise ValueError(f"{self.path.name}:{line}: 成功時の期待結果が不正です")
        if success == "false" and (stdout or not error):
            raise ValueError(f"{self.path.name}:{line}: 失敗時の期待結果が不正です")
        return CLIStartCase(
            case_id, BackendState(state), title, stdout, error, success == "true"
        )

    def validate_cases(self, cases: list[CLIStartCase]) -> None:
        identifiers = [case.case_id for case in cases]
        if not cases or any(not identifier.strip() for identifier in identifiers):
            raise ValueError(f"{self.path.name}: 空のケースまたはケース名です")
        if len(set(identifiers)) != len(identifiers):
            raise ValueError(f"{self.path.name}: ケース名が重複しています")
