# AMUCS Nexus backend entry point.

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.notices import router as notices_router
from app.api.search import router as search_router
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import setup_logging

setup_logging(settings.log_level)

app = FastAPI(title=settings.project_name, version=settings.version)
app.state.settings = settings

app.include_router(health_router, prefix="/api")
app.include_router(notices_router, prefix="/api")
app.include_router(search_router, prefix="/api")

register_error_handlers(app)
