from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker
from worklog.adapters.database.activity_repository import SQLAlchemyActivityRepository
from worklog.adapters.database.models import Base
from worklog.application.start_activity import StartActivity


def test_it001_usecase_saves_activity_through_sqlalchemy(engine: Engine) -> None:
    Base.metadata.create_all(engine)
    repository = SQLAlchemyActivityRepository(sessionmaker(engine))
    start_activity = StartActivity(
        repository=repository,
        clock=lambda: datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
        new_id=lambda: UUID("11111111-1111-1111-1111-111111111111"),
    )

    started = start_activity.run("設計を書く")

    saved = repository.all()
    assert saved == [started]
