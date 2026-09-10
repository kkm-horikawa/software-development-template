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


class ApplicationFactory:
    def __init__(
        self,
        engine: Engine | None = None,
        clock: Callable[[], datetime] | None = None,
        new_id: Callable[[], UUID] | None = None,
    ) -> None:
        self.engine = engine
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.new_id = new_id or uuid4

    def __call__(self) -> FastAPI:
        return self.create()

    def create(self) -> FastAPI:
        database = self.prepare_database()
        repository = self.make_repository(database)
        start_activity = self.make_start_activity(repository)
        endpoint = self.make_endpoint(start_activity)
        return self.make_application(endpoint, repository)

    def prepare_database(self) -> Engine:
        database = self.engine or create_engine("sqlite:///./activities.sqlite3")
        Base.metadata.create_all(database)
        return database

    def make_repository(self, database: Engine) -> SQLAlchemyActivityRepository:
        sessions = sessionmaker(database, expire_on_commit=False)
        return SQLAlchemyActivityRepository(sessions)

    def make_start_activity(
        self, repository: SQLAlchemyActivityRepository
    ) -> StartActivity:
        return StartActivity(
            repository=repository,
            clock=self.clock,
            new_id=self.new_id,
        )

    def make_endpoint(self, start_activity: StartActivity) -> ActivityEndpoint:
        return ActivityEndpoint(start_activity)

    def make_application(
        self,
        endpoint: ActivityEndpoint,
        repository: SQLAlchemyActivityRepository,
    ) -> FastAPI:
        app = FastAPI(title="Worklog API")
        app.add_api_route(
            "/activities",
            endpoint.post_activity,
            methods=["POST"],
            status_code=201,
            response_model=ActivityResponse,
        )
        app.add_exception_handler(EmptyActivityTitle, self.handle_empty_title)
        app.state.activity_repository = repository
        return app

    def handle_empty_title(
        self, _request: Request, error: EmptyActivityTitle
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(error)})


factory = ApplicationFactory()
