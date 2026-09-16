# API tests for the health endpoint and global error handling.
#
# FastAPI TestClient drives the application without a real web server,
# so these tests are fast and need no network.

from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.core.errors import AppError
from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["application"] == "AMUCS Nexus"


def test_health_reports_version_and_environment() -> None:
    resp = client.get("/api/health")
    data = resp.json()
    assert "version" in data
    assert "environment" in data


def test_unknown_route_returns_json_404() -> None:
    resp = client.get("/api/not-a-route")
    assert resp.status_code == 404
    assert "detail" in resp.json()


def test_app_error_returns_safe_json() -> None:
    # Register a throwaway route that raises our controlled error type to
    # prove the AppError handler returns a clean JSON payload.
    probe = APIRouter()

    @probe.get("/_probe/boom")
    def boom() -> None:
        raise AppError("controlled failure", status_code=400)

    app.include_router(probe)
    resp = client.get("/_probe/boom")
    assert resp.status_code == 400
    assert resp.json() == {"detail": "controlled failure"}
