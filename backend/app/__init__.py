# AMUCS Nexus backend package.

# Import the bootstrap first so the monorepo root is on sys.path before any
# `app.*` submodule imports the shared `ai` package (e.g. services.search).
from app import bootstrap as _bootstrap  # noqa: F401
