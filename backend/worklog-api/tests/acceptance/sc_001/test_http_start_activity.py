from fastapi import FastAPI
from fastapi.testclient import TestClient

from .cases import EMPTY_TITLE, NORMAL_TITLE


def test_sc001_ex01_http_returns_started_activity(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.post("/activities", json={"title": NORMAL_TITLE.title})

    assert response.status_code == NORMAL_TITLE.status_code
    assert response.json() == NORMAL_TITLE.response


def test_sc001_ex03_http_rejects_empty_title(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.post("/activities", json={"title": EMPTY_TITLE.title})

    assert response.status_code == EMPTY_TITLE.status_code
    assert response.json() == EMPTY_TITLE.response
