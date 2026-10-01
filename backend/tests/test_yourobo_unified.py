# Unified YouRobo retrieval, private uploads, and live notice sync tests.

from datetime import datetime
from uuid import UUID

import httpx
import pytest
import app.models  # noqa: F401
from app.core.database import Base, get_db
from app.main import app
from app.models.chat_upload import ChatUpload
from app.models.exam_resource import ExamResource
from app.models.faculty import Faculty
from app.models.laboratory import Laboratory
from app.models.notice import Notice
from app.services.chat import answer_question
from app.services.notice_sync import sync_notices
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

_engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(_engine)
with Session(_engine) as seed:
    seed.add(Faculty(
        name="Prof. Arman Rasool Faridi",
        designation="Chairperson and Professor",
        department="computer-science",
        email="ar.faridi.cs@amu.ac.in",
        profile_url="https://www.amu.ac.in/faculty/iceci-2026/arman-rasool-faridi",
        source_url="https://www.amu.ac.in/department/computer-science/faculty-members",
        specializations=[],
        research_areas=[],
    ))
    seed.add(Laboratory(
        name="Research Lab",
        description="A laboratory with GPU workstations for student research.",
        source_url="https://www.amu.ac.in/department/computer-science/important-laboratories",
    ))
    seed.add(ExamResource(
        title="Examination Results",
        category="official_resource",
        description="Official public result and grade lookup portal.",
        url="https://results.amucontrollerexams.com/",
        source_url="https://www.amucontrollerexams.com/",
    ))
    seed.commit()

client = TestClient(app)


def override_get_db():
    db = Session(_engine)
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def isolate_database(monkeypatch):
    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr("app.services.uploads._embed", lambda texts: None)
    monkeypatch.setattr("app.services.chat._configured_client", lambda: None)
    yield
    app.dependency_overrides.pop(get_db, None)


def test_faculty_lookup_tolerates_student_spelling() -> None:
    response = client.post("/api/chat", json={"question": "Who is Armaan Rasool Faridi?"})
    assert response.status_code == 200
    data = response.json()
    assert "Arman Rasool Faridi" in data["answer"]
    assert "ar.faridi.cs@amu.ac.in" in data["answer"]
    assert data["sources"][0]["source_type"] == "faculty"
    assert "[1]" in data["answer"]


def test_broad_laboratory_question_returns_laboratory_rows() -> None:
    response = client.post("/api/chat", json={"question": "What are the department laboratories?"})
    assert response.status_code == 200
    data = response.json()
    assert data["sources"]
    assert {source["source_type"] for source in data["sources"]} == {"laboratory"}
    assert "Research Lab" in data["answer"]


def test_exam_question_returns_exam_rows() -> None:
    response = client.post("/api/chat", json={"question": "How can I check an examination result?"})
    assert response.status_code == 200
    data = response.json()
    assert data["sources"]
    assert {source["source_type"] for source in data["sources"]} == {"exam"}
    assert "Examination Results" in data["answer"]


def test_unknown_question_has_no_sources_and_no_model_call() -> None:
    response = client.post("/api/chat", json={"question": "zzzz quantum submarine"})
    assert response.status_code == 200
    assert response.json()["sources"] == []
    assert "could not verify" in response.json()["answer"]


def test_private_text_upload_can_be_questioned_and_deleted() -> None:
    upload_response = client.post(
        "/api/chat/uploads",
        files={"file": ("dsa-notes.txt", b"DSA binary search tree notes. A binary search tree keeps keys ordered.", "text/plain")},
    )
    assert upload_response.status_code == 201
    upload = upload_response.json()
    assert upload["chunk_count"] >= 1

    payload = {
        "question": "What keeps keys ordered in a binary search tree?",
        "upload_id": upload["id"],
        "upload_token": upload["access_token"],
    }
    answer = client.post("/api/chat", json=payload)
    assert answer.status_code == 200
    assert "binary search tree" in answer.json()["answer"].lower()
    assert answer.json()["sources"][0]["source_type"] == "upload"

    wrong = client.post("/api/chat", json={**payload, "upload_token": "x" * 40})
    assert wrong.status_code == 403

    removed = client.delete(
        f"/api/chat/uploads/{upload['id']}",
        headers={"X-Upload-Token": upload["access_token"]},
    )
    assert removed.status_code == 200
    with Session(_engine) as db:
        assert db.get(ChatUpload, UUID(upload["id"])) is None


def test_gemini_embedding_key_never_reuses_groq_key(monkeypatch) -> None:
    from app.core import config

    monkeypatch.setattr(config.settings, "embedding_api_key", None)
    monkeypatch.setattr(config.settings, "gemini_api_key", None)
    monkeypatch.setattr(config.settings, "llm_api_key", "legacy-gemini-key")
    monkeypatch.setattr(config.settings, "groq_api_key", "legacy-gemini-key")
    assert config.gemini_embedding_key() is None
    monkeypatch.setattr(config.settings, "groq_api_key", "different-groq-key")
    assert config.gemini_embedding_key() == "legacy-gemini-key"
    monkeypatch.setattr(config.settings, "gemini_api_key", "explicit-gemini-key")
    assert config.gemini_embedding_key() == "explicit-gemini-key"


def test_notice_sync_creates_only_new_rows() -> None:
    payload = {"data": {"data": [{
        "title": "New examination schedule",
        "file": "/api/v1/file/3/notice/new.pdf",
        "created_at": "2026-09-25T10:00:00Z",
    }]}}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    with httpx.Client(transport=transport) as remote:
        with Session(_engine) as db:
            created = sync_notices(db, remote)
            assert len(created) == 1
            assert created[0].category == "examinations"
            assert sync_notices(db, remote) == []
            assert db.scalar(select(Notice).where(Notice.title == "New examination schedule")) is not None


def test_expired_upload_is_purged_without_notice_sync() -> None:
    from app.services.uploads import purge_expired_uploads

    with Session(_engine) as db:
        expired = ChatUpload(
            access_token_hash="expired-hash",
            filename="expired.txt",
            content_type="text/plain",
            size_bytes=10,
            expires_at=datetime(2020, 1, 1),
        )
        db.add(expired)
        db.commit()
        expired_id = expired.id
        assert purge_expired_uploads(db) == 1
        db.expunge_all()
        with Session(_engine) as fresh:
            assert fresh.get(ChatUpload, expired_id) is None


def test_real_notice_survives_sample_cleanup() -> None:
    from scripts.ingest_real import clear_sample_data

    with Session(_engine) as db:
        real = Notice(title="Real AMU notice", url="https://amu.ac.in/real-notice", category="general")
        sample = Notice(title="Mid-semester examination schedule", url="https://amu.ac.in/sample", category="examinations")
        db.add_all([real, sample])
        db.commit()
        real_id, sample_id = real.id, sample.id
        clear_sample_data(db)
        assert db.get(Notice, real_id) is not None
        assert db.get(Notice, sample_id) is None
