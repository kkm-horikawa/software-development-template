from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


class EmptyActivityTitle(ValueError):
    pass


@dataclass(frozen=True)
class ActivityTitle:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise EmptyActivityTitle("作業名を空にはできません")
        object.__setattr__(self, "value", normalized)

    @classmethod
    def create(cls, raw: str) -> "ActivityTitle":
        return cls(raw)


@dataclass(frozen=True)
class Activity:
    activity_id: UUID
    title: ActivityTitle
    started_at: datetime

    @classmethod
    def start(
        cls,
        activity_id: UUID,
        title: ActivityTitle,
        started_at: datetime,
    ) -> "Activity":
        return cls(activity_id=activity_id, title=title, started_at=started_at)
