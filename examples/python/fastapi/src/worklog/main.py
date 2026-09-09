from collections.abc import Callable
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from worklog.adapters.database.activity_repository import SQLAlchemyActivityRepository
from worklog.adapters.database.models import Base
from worklog.adapters.http.activity_endpoint import ActivityEndpoint
from worklog.adapters.http.schemas import ActivityResponse
from worklog.application.start_activity import StartActivity
from worklog.domain.activity import EmptyActivityTitle


def create_app(
    engine: Engine | None = None,
    clock: Callable[[], datetime] | None = None,
    new_id: Callable[[], UUID] | None = None,
) -> FastAPI:
    database = engine or create_engine("sqlite:///./activities.sqlite3")
    Base.metadata.create_all(database)
    sessions = sessionmaker(database, expire_on_commit=False)
    repository = SQLAlchemyActivityRepository(sessions)
    start_activity = StartActivity(
        repository=repository,
        clock=clock or (lambda: datetime.now(timezone.utc)),
        new_id=new_id or uuid4,
    )
    endpoint = ActivityEndpoint(start_activity)

    app = FastAPI(title="Top-down activity example")
    app.add_api_route(
        "/activities",
        endpoint.post_activity,
        methods=["POST"],
        status_code=201,
        response_model=ActivityResponse,
    )

    @app.exception_handler(EmptyActivityTitle)
    def handle_empty_title(
        _request: Request, error: EmptyActivityTitle
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(error)})

    app.state.activity_repository = repository
    return app
