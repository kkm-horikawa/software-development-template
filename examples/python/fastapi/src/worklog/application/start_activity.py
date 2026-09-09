from collections.abc import Callable
from datetime import datetime
from uuid import UUID

from worklog.domain.activity import Activity, ActivityTitle
from worklog.ports.activity_repository import ActivityRepository


class StartActivity:
    def __init__(
        self,
        repository: ActivityRepository,
        clock: Callable[[], datetime],
        new_id: Callable[[], UUID],
    ) -> None:
        self._repository = repository
        self._clock = clock
        self._new_id = new_id

    def run(self, raw_title: str) -> Activity:
        title = self._make_title(raw_title)
        activity = self._start_activity(title)
        self._save_activity(activity)
        return activity

    def _make_title(self, raw_title: str) -> ActivityTitle:
        return ActivityTitle.create(raw_title)

    def _start_activity(self, title: ActivityTitle) -> Activity:
        return Activity.start(
            activity_id=self._new_id(),
            title=title,
            started_at=self._clock(),
        )

    def _save_activity(self, activity: Activity) -> None:
        self._repository.save(activity)
