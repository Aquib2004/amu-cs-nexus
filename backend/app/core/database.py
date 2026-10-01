# Database engine, session factory, and declarative base.
#
# Production uses PostgreSQL via DATABASE_URL. For local development with
# no database server installed, we fall back to a local SQLite file so the
# app and tests can run immediately. SQLite lets us develop the models and
# repositories; PostgreSQL remains the production target.

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# Local development fallback when DATABASE_URL is not set.
DEFAULT_DEV_URL = "sqlite:///./amucs_nexus_dev.db"


def _engine_options(url: str) -> dict:
    # Options are chosen per backend: SQLite needs relaxed thread checks,
    # while PostgreSQL gets a bounded pool and connection recycling.
    options: dict = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False, "timeout": 30}
    else:
        options.update(
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
        )
    return options


# Resolve the URL once. SQLAlchemy connects lazily, so importing this
# module does not require a database server to be running.
database_url = settings.database_url or DEFAULT_DEV_URL
engine = create_engine(database_url, **_engine_options(database_url))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Declarative base that all ORM models inherit from."""


def get_db():
    """FastAPI dependency that provides one session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
