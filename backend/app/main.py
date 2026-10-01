# AMUCS Nexus backend entry point.

from __future__ import annotations

import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.faculty import router as faculty_router
from app.api.health import router as health_router
from app.api.exams import router as exams_router
from app.api.laboratories import router as laboratories_router
from app.api.notifications import router as notifications_router
from app.api.notices import router as notices_router
from app.api.programs import router as programs_router
from app.api.research import router as research_router
from app.api.research_projects import router as research_projects_router
from app.api.search import router as search_router
from app.api.staff import router as staff_router
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import setup_logging
from app.core.tls import describe_tls


logger = logging.getLogger(__name__)


async def _notice_loop() -> None:
    from app.core.database import SessionLocal
    from app.services.notice_sync import run_notice_cycle

    while True:
        try:
            # Each cycle gets its own session and always closes it, so a failed
            # sync cannot leak connections or stop the loop.
            session = SessionLocal()
        except Exception:
            logging.getLogger(__name__).exception("Could not open a database session for notice sync")
            await asyncio.sleep(settings.notice_sync_interval_seconds)
            continue
        try:
            await asyncio.to_thread(run_notice_cycle, session)
        except asyncio.CancelledError:
            session.close()
            raise
        except Exception:
            logging.getLogger(__name__).exception("Notice synchronization cycle failed")
        finally:
            session.close()
        await asyncio.sleep(settings.notice_sync_interval_seconds)


async def _upload_cleanup_loop() -> None:
    from app.core.database import SessionLocal
    from app.services.uploads import purge_expired_uploads

    while True:
        await asyncio.sleep(settings.upload_cleanup_interval_seconds)
        session = SessionLocal()
        try:
            removed = await asyncio.to_thread(purge_expired_uploads, session)
            if removed:
                logging.getLogger(__name__).info("Purged %d expired upload(s)", removed)
        except Exception:
            logging.getLogger(__name__).exception("Expired-upload cleanup failed")
        finally:
            session.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    from app.core.database import SessionLocal
    from app.services.uploads import purge_expired_uploads

    _log_optional_features()
    notice_task = None
    cleanup_task = None
    if settings.notice_sync_enabled:
        notice_task = asyncio.create_task(_notice_loop())
    cleanup_task = asyncio.create_task(_upload_cleanup_loop())
    # Remove already-expired uploads immediately on startup, then continue on
    # the interval above. This keeps privacy guarantees independent of notice sync.
    startup_session = SessionLocal()
    try:
        await asyncio.to_thread(purge_expired_uploads, startup_session)
    finally:
        startup_session.close()
    yield
    for task in (notice_task, cleanup_task):
        if task:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task


setup_logging(settings.log_level)


def _cors_origins() -> list[str]:
    """Resolve allowed origins, never falling back to a wildcard.

    An unset or empty CORS_ORIGINS keeps the local development default so a
    fresh clone works, but production must set it explicitly.
    """
    configured = [origin.strip() for origin in (settings.cors_origins or "").split(",") if origin.strip()]
    if not configured:
        if settings.environment.lower() == "production":
            logger.warning(
                "CORS_ORIGINS is not set in production; no cross-origin browser requests will be allowed."
            )
            return []
        logger.warning(
            "CORS_ORIGINS is not set; defaulting to http://localhost:3000 for local development."
        )
        return ["http://localhost:3000"]
    if "*" in configured:
        raise RuntimeError("CORS_ORIGINS must not contain '*'; list explicit origins instead.")
    return configured


def _log_optional_features() -> None:
    """Log which optional integrations are disabled so ops can see the state."""
    if not (settings.llm_api_key or settings.gemini_api_key or settings.groq_api_key):
        logger.info("LLM provider keys not set; using extractive fallback")
    if not (settings.embedding_api_key or settings.gemini_api_key):
        logger.info("Embedding provider key not set; storing raw text chunks")
    if not (settings.vapid_private_key or settings.vapid_private_key_file):
        logger.info("Web Push notifications disabled")
    logger.info("Outbound TLS trust store: %s (verification enabled)", describe_tls())


app = FastAPI(title=settings.project_name, version=settings.version, lifespan=lifespan)
app.state.settings = settings

from app.core.database import engine  # noqa: E402

app.state.engine = engine

# Allow the Next.js frontend (and any configured origin) to call the API from the
# browser. Origins come from settings.cors_origins (comma-separated string).
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
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
app.include_router(exams_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")

register_error_handlers(app)