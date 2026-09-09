from worklog.adapters.http.schemas import ActivityResponse, StartActivityRequest
from worklog.application.start_activity import StartActivity
from worklog.domain.activity import Activity


class ActivityEndpoint:
    def __init__(self, start_activity: StartActivity) -> None:
        self._start_activity = start_activity

    def post_activity(self, request: StartActivityRequest) -> ActivityResponse:
        title = self._read_title(request)
        activity = self._start_work(title)
        return self._write_activity(activity)

    def _read_title(self, request: StartActivityRequest) -> str:
        return request.title

    def _start_work(self, title: str) -> Activity:
        return self._start_activity.run(title)

    def _write_activity(self, activity: Activity) -> ActivityResponse:
        return ActivityResponse(
            id=activity.activity_id,
            title=activity.title.value,
            started_at=activity.started_at,
        )
