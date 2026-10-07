# AMUCS Nexus backend entry point.

from __future__ import annotations

import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware

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
from app.core.config import gemini_embedding_key, settings
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
        # Opening the session inside its own try is deliberate: if
        # SessionLocal() itself raises, this loop must keep running. Otherwise a
        # single failure silently kills the task and expired uploads accumulate
        # forever, which is a privacy failure and not merely a performance one.
        try:
            session = SessionLocal()
        except Exception:
            logging.getLogger(__name__).exception(
                "Could not open a database session for upload cleanup"
            )
            continue
        try:
            removed = await asyncio.to_thread(purge_expired_uploads, session)
            if removed:
                logging.getLogger(__name__).info("Purged %d expired upload(s)", removed)
        except asyncio.CancelledError:
            session.close()
            raise
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
    if not gemini_embedding_key():
        logger.info("Embedding provider key not set; storing raw text chunks")
    else:
        logger.info("Embedding provider key detected; chunks are embedded on ingest")
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


# --- Frontend ---------------------------------------------------------------
# The statically exported site (frontend/out) is served from this same app, so
# the UI and the API share one origin and the browser never issues a
# cross-origin request. That is what makes the deployed site work without a
# CORS_ORIGINS entry for the frontend: there is no second origin to allowlist.
#
# The export is committed to the repo because Render's Python runtime has no
# Node and therefore cannot run `next build` during deploy.
_FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend" / "out"
# Paths that must never be answered from disk: they are the API itself, and
# /docs etc. are generated by FastAPI.
_FRONTEND_PASSTHROUGH = ("/api", "/docs", "/redoc", "/openapi.json")


def _frontend_file(url_path: str) -> Path | None:
    """Map a request path onto a file in the export, or None if there is none.

    Handles the three shapes a static export produces: the directory index
    ("/" and "/chat/"), the bare directory ("/chat"), and a real asset. The
    resolve()+relative_to() pair rejects "../" escapes out of the export.
    """
    if not _FRONTEND_DIR.is_dir():
        return None
    root = _FRONTEND_DIR.resolve()
    relative = url_path.lstrip("/")
    names = [relative or "index.html"]
    if not relative or relative.endswith("/"):
        names.append(f"{relative}index.html")
    else:
        names.extend((f"{relative}/index.html", f"{relative}.html"))
    for name in names:
        try:
            candidate = (root / name).resolve()
            candidate.relative_to(root)
        except (OSError, ValueError):
            continue
        if candidate.is_file():
            return candidate
    return None


class _ServeFrontend(BaseHTTPMiddleware):
    """Serve the export when a file matches, otherwise fall through untouched.

    This is deliberately NOT a mount on "/". A mount owns every path it
    matches, which broke two things the tests catch: unknown API routes stopped
    returning JSON 404 (the exported 404.html won instead), and any router
    registered after import - which is how the error handlers are probed - was
    shadowed by the mount. Only handling paths that resolve to a real file
    leaves API routing and error handling exactly as they were.
    """

    async def dispatch(self, request: Request, call_next):  # noqa: ANN201
        if request.method not in ("GET", "HEAD"):
            return await call_next(request)
        path = request.url.path
        if path.startswith(_FRONTEND_PASSTHROUGH):
            return await call_next(request)
        target = _frontend_file(path)
        if target is None:
            return await call_next(request)
        return FileResponse(target)


if _FRONTEND_DIR.is_dir():
    app.add_middleware(_ServeFrontend)
else:
    # Local clones without a build still get a working API; only the UI 404s.
    logger.warning("Frontend export not found at %s; serving the API only", _FRONTEND_DIR)
