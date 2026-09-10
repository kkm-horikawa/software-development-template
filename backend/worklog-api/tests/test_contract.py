import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker
from sqlalchemy import Engine
from worklog.adapters.database.models import Base

ROOT = Path(__file__).resolve().parents[3]


class TestPublishedContract:
    def test_published_openapi_matches_backend(self, app: FastAPI) -> None:
        assert app.openapi() == self.contract()

    @pytest.mark.parametrize(
        "payload,expected_status",
        [
            ({"title": "設計を書く"}, 201),
            ({"title": "   "}, 422),
            ({}, 422),
            ({"title": None}, 422),
            ({"title": 123}, 422),
        ],
    )
    def test_actual_responses_follow_published_contract(
        self, app: FastAPI, payload: dict[str, object], expected_status: int
    ) -> None:
        with TestClient(app) as client:
            response = client.post("/activities", json=payload)
        assert response.status_code == expected_status
        self.assert_response(response.status_code, response.json())

    def test_storage_failure_follows_published_contract(
        self, app: FastAPI, engine: Engine
    ) -> None:
        Base.metadata.drop_all(engine)
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.post("/activities", json={"title": "設計を書く"})
        assert response.status_code == 503
        self.assert_response(response.status_code, response.json())

    def assert_response(self, status: int, payload: object) -> None:
        contract = self.contract()
        schema = contract["paths"]["/activities"]["post"]["responses"][str(status)][
            "content"
        ]["application/json"]["schema"]
        Draft202012Validator(
            {**schema, "components": contract["components"]},
            format_checker=FormatChecker(),
        ).validate(payload)

    def contract(self) -> dict[str, object]:
        return json.loads(
            (ROOT / "contracts/worklog-api.openapi.json").read_text(encoding="utf-8")
        )
