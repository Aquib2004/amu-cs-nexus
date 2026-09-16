# Health check endpoints.
#
# A health endpoint lets load balancers, uptime monitors, and the
# frontend confirm the API is running. It holds no business logic.

from fastapi import APIRouter

# APIRouter groups related endpoints. It is mounted into the app in main.py.
router = APIRouter(tags=["health"])  # type: ignore


@router.get("/health")
def health() -> dict[str, str]:
    """Return service status."""
    return {"status": "ok"}
