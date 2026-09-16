# Health check endpoint.
#
# The health endpoint has no business logic. It confirms the service is
# running and reports basic application identity from settings, so uptime
# monitors, load balancers, and the frontend can check the API.

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
def health(request: Request) -> dict[str, str]:
    """Return service status and basic identity."""
    settings = request.app.state.settings
    return {
        "status": "ok",
        "application": settings.project_name,
        "version": settings.version,
        "environment": settings.environment,
    }
