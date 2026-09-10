from dataclasses import dataclass


@dataclass(frozen=True)
class HTTPStartCase:
    title: str
    status_code: int
    response: dict[str, str]


NORMAL_TITLE = HTTPStartCase(
    title="  設計を書く  ",
    status_code=201,
    response={
        "id": "11111111-1111-1111-1111-111111111111",
        "title": "設計を書く",
        "started_at": "2026-09-09T10:00:00Z",
    },
)

EMPTY_TITLE = HTTPStartCase(
    title="   ",
    status_code=422,
    response={"detail": "作業名を空にはできません"},
)
