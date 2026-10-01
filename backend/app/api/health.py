# Health check endpoint.
#
# The endpoint reports service identity plus a live database probe so uptime
# monitors and the frontend can tell "process is up" from "dependencies work".
# The probe never returns driver or connection details to the client.

from fastapi import APIRouter, Request
from sqlalchemy import text

from app.core.logging import get_logger
from app.schemas.health import HealthResponse

logger = get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    """Return service identity and database connectivity without leaking errors."""
    settings = request.app.state.settings
    database = "ok"
    status = "ok"
    try:
        with request.app.state.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:  # pragma: no cover - depends on real infrastructure
        logger.exception("Database health probe failed")
        database = "unavailable"
        status = "degraded"
    return HealthResponse(
        status=status,
        application=settings.project_name,
        version=settings.version,
        environment=settings.environment,
        database=database,
    )