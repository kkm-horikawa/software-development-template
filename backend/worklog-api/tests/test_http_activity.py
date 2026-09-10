from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_st_1_01_http_entry_starts_and_saves_activity(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.post("/activities", json={"title": "  設計を書く  "})

    assert response.status_code == 201
    assert response.json() == {
        "id": "11111111-1111-1111-1111-111111111111",
        "title": "設計を書く",
        "started_at": "2026-09-09T10:00:00Z",
    }
    saved = app.state.activity_repository.all()
    assert len(saved) == 1
    assert saved[0].title.value == "設計を書く"


def test_http_entry_translates_empty_title_to_client_error(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.post("/activities", json={"title": "   "})

    assert response.status_code == 422
    assert response.json() == {"detail": "作業名を空にはできません"}
