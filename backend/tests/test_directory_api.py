# API tests for /api/faculty and /api/documents with an isolated SQLite DB.

import pytest
import app.models  # noqa: F401
from app.core.database import Base, get_db
from app.main import app
from app.models.document import Chunk, Document
from app.models.faculty import Faculty
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
_seed.add(
    Faculty(
        name="Dr. S. Begum",
        title="Assistant Professor",
        department="computer-science",
        email="sbegum@amu.ac.in",
        specializations=["Machine Learning"],
        research_areas=["Deep Learning"],
    )
)
_doc = Document(
    title="Vision Research",
    source_url="https://amu.ac.in/vision",
    department="computer-science",
    source_type="web",
    document_type="publication",
)
_doc.chunks.append(Chunk(chunk_index=0, text="transformer architectures"))
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


def test_faculty_list_and_get() -> None:
    resp = client.get("/api/faculty")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    fid = data[0]["id"]
    one = client.get(f"/api/faculty/{fid}")
    assert one.status_code == 200
    assert one.json()["email"] == "sbegum@amu.ac.in"
    assert one.json()["specializations"] == ["Machine Learning"]


def test_faculty_not_found() -> None:
    resp = client.get("/api/faculty/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_documents_list_and_detail() -> None:
    resp = client.get("/api/documents")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert "title" in data[0] and "chunks" not in data[0]  # list is metadata only
    doc_id = data[0]["id"]
    detail = client.get(f"/api/documents/{doc_id}")
    assert detail.status_code == 200
    assert detail.json()["source_url"] == "https://amu.ac.in/vision"
    assert len(detail.json()["chunks"]) == 1


def test_research_endpoint_filters_publications() -> None:
    resp = client.get("/api/research")
    assert resp.status_code == 200
    data = resp.json()
    assert all(d["document_type"] in ("research", "publication") for d in data)