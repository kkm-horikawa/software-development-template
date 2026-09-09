from collections.abc import Iterator
from datetime import datetime, timezone
from uuid import UUID

import pytest
from fastapi import FastAPI
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool
from worklog.main import create_app

FIXED_TIME = datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc)
FIXED_ID = UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def engine() -> Iterator[Engine]:
    database = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield database
    database.dispose()


@pytest.fixture
def app(engine: Engine) -> FastAPI:
    return create_app(
        engine=engine,
        clock=lambda: FIXED_TIME,
        new_id=lambda: FIXED_ID,
    )
