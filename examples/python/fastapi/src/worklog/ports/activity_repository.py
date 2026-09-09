from typing import Protocol

from worklog.domain.activity import Activity


class ActivityRepository(Protocol):
    def save(self, activity: Activity) -> None: ...
