from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from .cases import HTTPStartCase, HTTPStartCases


class TestHTTPStartActivity:
    @pytest.mark.parametrize(
        "case",
        HTTPStartCases(Path(__file__).with_name("task.csv")).load(),
        ids=lambda case: case.case_id,
    )
    def test_http_start_activity(self, app: FastAPI, case: HTTPStartCase) -> None:
        with TestClient(app) as client:
            response = client.post("/activities", json={"title": case.title})

        assert response.status_code == case.status_code
        assert response.json() == case.response()
