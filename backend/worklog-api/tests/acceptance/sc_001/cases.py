import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HTTPStartCase:
    case_id: str
    title: str
    status_code: int
    expected_id: str
    expected_title: str
    expected_started_at: str
    expected_error: str

    def response(self) -> dict[str, str]:
        if self.expected_error:
            return {"detail": self.expected_error}
        return {
            "id": self.expected_id,
            "title": self.expected_title,
            "started_at": self.expected_started_at,
        }


class HTTPStartCases:
    COLUMNS = (
        "case_id",
        "title",
        "status_code",
        "expected_id",
        "expected_title",
        "expected_started_at",
        "expected_error",
    )

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> list[HTTPStartCase]:
        with self.path.open(encoding="utf-8", newline="") as source:
            reader = csv.reader(source, strict=True)
            self.validate_header(next(reader, []))
            cases = [self.read_case(row, reader.line_num) for row in reader]
        self.validate_cases(cases)
        return cases

    def validate_header(self, header: list[str]) -> None:
        if tuple(header) != self.COLUMNS:
            raise ValueError(f"{self.path.name}: CSVの列が想定と一致しません: {header}")

    def read_case(self, row: list[str], line: int) -> HTTPStartCase:
        if len(row) != len(self.COLUMNS):
            raise ValueError(f"{self.path.name}:{line}: CSVの列数が一致しません")
        case_id, title, status, identifier, expected_title, started_at, error = row
        if status not in {"201", "422"}:
            raise ValueError(f"{self.path.name}:{line}: 未対応の応答状態: {status}")
        success_values = (identifier, expected_title, started_at)
        if status == "201" and (not all(success_values) or error):
            raise ValueError(f"{self.path.name}:{line}: 成功時の期待結果が不正です")
        if status == "422" and (any(success_values) or not error):
            raise ValueError(f"{self.path.name}:{line}: 失敗時の期待結果が不正です")
        return HTTPStartCase(
            case_id, title, int(status), identifier, expected_title, started_at, error
        )

    def validate_cases(self, cases: list[HTTPStartCase]) -> None:
        identifiers = [case.case_id for case in cases]
        if not cases or any(not identifier.strip() for identifier in identifiers):
            raise ValueError(f"{self.path.name}: 空のケースまたはケース名です")
        if len(set(identifiers)) != len(identifiers):
            raise ValueError(f"{self.path.name}: ケース名が重複しています")
