"""Request validation tests for public API endpoints.

Every test here asserts an HTTP status only, so no real database is touched:
FastAPI rejects malformed input before the route body runs.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (registers tables on Base.metadata)
from app.core.database import Base
from app.main import app
from app.models.document import Chunk, Document
from app.services.search import search_chunks

client = TestClient(app)

# A small in-memory corpus keeps relevance assertions deterministic and stops
# these tests from reading the real development database.
_engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(_engine)
_session = Session(_engine, expire_on_commit=False)
_doc = Document(
    title="Vision Research",
    source_url="https://amu.ac.in/vision",
    department="computer-science",
    document_type="publication",
)
_doc.chunks.append(
    Chunk(chunk_index=0, text="papers about computer vision and image processing")
)
_session.add(_doc)
_session.commit()


@pytest.mark.parametrize(
    "params",
    [
        {"q": ""},
        {"q": "x" * 301},
        {"q": "vision", "limit": 0},
        {"q": "vision", "limit": 51},
        {"q": "vision", "limit": "not-a-number"},
    ],
)
def test_search_rejects_out_of_range_input(params: dict[str, object]) -> None:
    assert client.get("/api/search", params=params).status_code == 422


def test_search_returns_empty_list_for_no_match() -> None:
    """A nonsense query must return [], not the least-unrelated chunk."""
    assert search_chunks(_session, query="zzzznothingq") == []


def test_search_is_deterministic_for_the_same_query() -> None:
    first = search_chunks(_session, query="vision", limit=5)
    second = search_chunks(_session, query="vision", limit=5)
    assert [r.chunk_id for r in first] == [r.chunk_id for r in second]


def test_search_ignores_an_unknown_metadata_filter() -> None:
    assert search_chunks(_session, query="vision", department="not-a-department") == []


@pytest.mark.parametrize(
    "payload",
    [
        {"question": ""},
        {"question": "x" * 501},
        {"question": "Who is the faculty?", "limit": 0},
        {"question": "Who is the faculty?", "limit": 21},
        {},
    ],
)
def test_chat_rejects_out_of_range_input(payload: dict[str, object]) -> None:
    assert client.post("/api/chat", json=payload).status_code == 422


def test_chat_rejects_invalid_json_body() -> None:
    resp = client.post(
        "/api/chat",
        content=b"{not json",
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 422


@pytest.mark.parametrize(
    "path",
    [
        "/api/notices/not-a-uuid",
        "/api/faculty/not-a-uuid",
        "/api/documents/not-a-uuid",
        "/api/exams/not-a-uuid",
    ],
)
def test_detail_endpoints_reject_invalid_uuid(path: str) -> None:
    assert client.get(path).status_code == 422


@pytest.mark.parametrize(
    "path",
    ["/api/notices", "/api/faculty", "/api/documents", "/api/programs", "/api/staff"],
)
@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 1000}, {"offset": -1}])
def test_list_endpoints_reject_out_of_range_pagination(
    path: str, params: dict[str, int]
) -> None:
    assert client.get(path, params=params).status_code == 422


def test_chat_upload_delete_requires_a_token_header() -> None:
    resp = client.delete("/api/chat/uploads/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 422


def test_chat_rejects_upload_id_without_token() -> None:
    resp = client.post(
        "/api/chat",
        json={
            "question": "What is this?",
            "upload_id": "00000000-0000-0000-0000-000000000000",
        },
    )
    assert resp.status_code == 422


def test_chat_rejects_short_upload_token() -> None:
    resp = client.post(
        "/api/chat",
        json={
            "question": "What is this?",
            "upload_id": "00000000-0000-0000-0000-000000000000",
            "upload_token": "short",
        },
    )
    assert resp.status_code == 422
