# API tests for /api/chat with an isolated in-memory SQLite database.

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
    title="MCA Admission - June 2024",
    source_url="https://amu.ac.in/mca-admission",
    department="computer-science",
    document_type="notice",
)
_doc.chunks.append(
    Chunk(chunk_index=0, text="The MCA admission notice was published in June 2024.")
)
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


def test_chat_returns_grounded_answer_with_source() -> None:
    resp = client.post(
        "/api/chat", json={"question": "When was the MCA admission notice published?"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "[1]" in data["answer"]
    assert data["sources"]
    assert data["sources"][0]["source_url"] == "https://amu.ac.in/mca-admission"


def test_chat_admits_when_unverifiable() -> None:
    resp = client.post("/api/chat", json={"question": "zzzz not in index"})
    assert resp.status_code == 200
    assert "not verify" in resp.json()["answer"]


def test_chat_validates_empty_question() -> None:
    resp = client.post("/api/chat", json={"question": ""})
    assert resp.status_code == 422
