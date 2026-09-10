import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from worklog.main import ApplicationFactory

database = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
app = ApplicationFactory(
    engine=database,
    clock=lambda: datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
    new_id=lambda: UUID("11111111-1111-1111-1111-111111111111"),
).create()

with TestClient(app) as client:
    response = client.post("/activities", json={"title": "設計を書く"})

print(f"POST /activities: {response.status_code}")
print(json.dumps(response.json(), ensure_ascii=False, separators=(",", ":")))
print(f"SQLAlchemy保存件数: {len(app.state.activity_repository.all())}")
