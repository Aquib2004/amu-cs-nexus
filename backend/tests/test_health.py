# API tests for the health endpoint and global error handling.
#
# FastAPI TestClient drives the application without a real web server,
# so these tests are fast and need no network.

from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.core.errors import AppError
from app.main import app

client = TestClient(app)
# The exception handler still raises through TestClient by default, so probe
# routes that intentionally fail are driven with a non-raising client.
non_raising_client = TestClient(app, raise_server_exceptions=False)


def test_health_returns_ok() -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["application"] == "AMUCS Nexus"
    assert data["database"] == "ok"


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

def test_health_reports_degraded_when_database_is_unavailable() -> None:
    """A dead database degrades the status instead of leaking driver errors."""
    from sqlalchemy.exc import OperationalError

    class BrokenEngine:
        def connect(self):
            raise OperationalError("connect", {}, Exception("no route to host"))

    original = app.state.engine
    app.state.engine = BrokenEngine()
    try:
        resp = client.get("/api/health")
    finally:
        app.state.engine = original
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "degraded"
    assert data["database"] == "unavailable"
    assert "no route to host" not in resp.text


def test_health_does_not_500_when_the_probe_raises() -> None:
    class ExplodingEngine:
        def connect(self):
            raise RuntimeError("internal detail")

    original = app.state.engine
    app.state.engine = ExplodingEngine()
    try:
        resp = client.get("/api/health")
    finally:
        app.state.engine = original
    assert resp.status_code == 200
    assert "internal detail" not in resp.text


def test_unhandled_exception_returns_generic_500() -> None:
    """Internal tracebacks must be logged, never returned to the client."""
    probe = APIRouter()

    @probe.get("/_probe/traceback")
    def traceback() -> None:
        raise RuntimeError("secret connection string leaked")

    app.include_router(probe)
    resp = non_raising_client.get("/_probe/traceback")
    assert resp.status_code == 500
    assert resp.json() == {"detail": "Internal server error"}
    assert "secret connection string" not in resp.text


def test_value_error_handler_returns_safe_400() -> None:
    probe = APIRouter()

    @probe.get("/_probe/badvalue")
    def bad_value() -> None:
        raise ValueError("untrusted internal detail")

    app.include_router(probe)
    resp = non_raising_client.get("/_probe/badvalue")
    assert resp.status_code == 400
    assert resp.json() == {"detail": "Invalid request value"}
    assert "untrusted internal detail" not in resp.text


def test_cors_preflight_allows_configured_origin() -> None:
    resp = client.options(
        "/api/search",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_does_not_reflect_unknown_origin() -> None:
    resp = client.get("/api/health", headers={"Origin": "https://evil.example.com"})
    assert resp.headers.get("access-control-allow-origin") != "https://evil.example.com"
