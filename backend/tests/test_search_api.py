# API tests for /api/search with an isolated in-memory SQLite database.

import pytest
import app.models  # noqa: F401
from app.core.database import Base, get_db
from app.main import app
from app.models.document import Chunk, Document
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

_engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(_engine)

_seed = Session(_engine, expire_on_commit=False)
_doc = Document(
    title="Vision Research",
    source_url="https://amu.ac.in/vision",
    department="computer-science",
    document_type="publication",
)
_doc.chunks.append(Chunk(chunk_index=0, text="papers about computer vision", embedding=[0.0] * 384))
_seed.add(_doc)
_seed.commit()
_seed.close()

client = TestClient(app)


def override_get_db():
    db = Session(_engine)
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _isolate_db_override():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


def test_search_returns_source_grounded_results() -> None:
    resp = client.get("/api/search", params={"q": "vision"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["source_url"] == "https://amu.ac.in/vision"
    assert "vision" in data[0]["text"].lower()


def test_search_with_metadata_filter() -> None:
    resp = client.get(
        "/api/search", params={"q": "vision", "department": "computer-science"}
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_search_no_match_returns_empty() -> None:
    resp = client.get("/api/search", params={"q": "zzzznothing"})
    assert resp.status_code == 200
    assert resp.json() == []
