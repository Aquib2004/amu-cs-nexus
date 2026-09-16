# AMUCS Nexus backend entry point.
#
# Creates the FastAPI application and wires together the foundation:
# configuration (settings), logging, error handling, and routers.

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.notices import router as notices_router
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import setup_logging

# Configure logging once, using the level from settings.
setup_logging(settings.log_level)

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
)

# Store settings on the app so route handlers can read configuration.
app.state.settings = settings

# Mount routers under the /api prefix.
app.include_router(health_router, prefix="/api")
app.include_router(notices_router, prefix="/api")

# Register global exception handlers: AppError -> safe JSON,
# anything else -> a logged 500 with a generic client message.
register_error_handlers(app)
