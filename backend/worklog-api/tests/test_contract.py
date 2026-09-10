import json
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from worklog.main import ApplicationFactory

ROOT = Path(__file__).resolve().parents[3]


def test_it004_published_openapi_matches_backend() -> None:
    database = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    actual = ApplicationFactory(engine=database).create().openapi()
    published = json.loads(
        (ROOT / "contracts/worklog-api.openapi.json").read_text(encoding="utf-8")
    )

    assert actual == published
