from datetime import timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from worklog.adapters.database.models import ActivityRow
from worklog.domain.activity import Activity, ActivityTitle


class SQLAlchemyActivityRepository:
    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self._sessions = sessions

    def save(self, activity: Activity) -> None:
        with self._sessions.begin() as session:
            session.add(
                ActivityRow(
                    id=str(activity.activity_id),
                    title=activity.title.value,
                    started_at=activity.started_at,
                )
            )

    def all(self) -> list[Activity]:
        with self._sessions() as session:
            rows = session.scalars(
                select(ActivityRow).order_by(ActivityRow.started_at)
            ).all()
        return [
            Activity(
                activity_id=UUID(row.id),
                title=ActivityTitle(row.title),
                started_at=(
                    row.started_at
                    if row.started_at.tzinfo is not None
                    else row.started_at.replace(tzinfo=timezone.utc)
                ),
            )
            for row in rows
        ]
