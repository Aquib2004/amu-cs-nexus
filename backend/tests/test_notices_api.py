# API tests for /api/notices with an isolated in-memory SQLite database.

from datetime import datetime
from uuid import uuid4

import pytest
import sqlalchemy as sa  # noqa: F401
import app.models  # noqa: F401
from app.core.database import Base, get_db
from app.main import app
from app.models.notice import Notice
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

_test_engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(_test_engine)

_seed_session = Session(_test_engine, expire_on_commit=False)
_notice1 = Notice(
    title="Holiday",
    url="https://amu.ac.in/notice/1",
    category="general",
    published_at=datetime(2026, 9, 1),
)
_notice2 = Notice(
    title="Exam",
    url="https://amu.ac.in/notice/2",
    category="examinations",
    published_at=datetime(2026, 9, 5),
)
_seed_session.add_all([_notice1, _notice2])
_seed_session.commit()
_seed_session.close()
NOTICE1_ID = str(_notice1.id)

client = TestClient(app)


def override_get_db():
    db = Session(_test_engine)
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _isolate_db_override():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


def test_list_notices() -> None:
    resp = client.get("/api/notices")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    titles = {item["title"] for item in data}
    assert {"Holiday", "Exam"} <= titles


def test_get_notice_found() -> None:
    resp = client.get(f"/api/notices/{NOTICE1_ID}")
    assert resp.status_code == 200
    assert resp.json()["id"] == NOTICE1_ID


def test_get_notice_not_found() -> None:
    resp = client.get(f"/api/notices/{uuid4()}")
    assert resp.status_code == 404
