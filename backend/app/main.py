# AMUCS Nexus backend entry point.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.faculty import router as faculty_router
from app.api.health import router as health_router
from app.api.laboratories import router as laboratories_router
from app.api.notices import router as notices_router
from app.api.programs import router as programs_router
from app.api.research import router as research_router
from app.api.research_projects import router as research_projects_router
from app.api.search import router as search_router
from app.api.staff import router as staff_router
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import setup_logging

setup_logging(settings.log_level)

app = FastAPI(title=settings.project_name, version=settings.version)
app.state.settings = settings

# Allow the Next.js frontend (and any configured origin) to call the API from the
# browser. Origins come from settings.cors_origins (comma-separated string).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(notices_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(faculty_router, prefix="/api")
app.include_router(research_router, prefix="/api")
app.include_router(programs_router, prefix="/api")
app.include_router(laboratories_router, prefix="/api")
app.include_router(research_projects_router, prefix="/api")
app.include_router(staff_router, prefix="/api")

register_error_handlers(app)