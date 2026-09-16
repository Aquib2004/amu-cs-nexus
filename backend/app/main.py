# AMUCS Nexus backend entry point.
#
# This module creates the FastAPI application and mounts the API routers.
# At repository initialization the only implemented route is the health
# check. Business endpoints (search, chat, notices, documents, faculty)
# will be added in later phases.

from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(
    title="AMUCS Nexus API",
    description="REST API for AMUCS Nexus.",
    version="0.1.0",
)

# Mount the health router under the /api prefix.
# The routerpath /api/health is reachable once the server runs.
app.include_router(health_router, prefix="/api")
