# Tests for the database layer (models + repositories) using an
# in-memory SQLite database, so they run with no external server.

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  - registers models on Base.metadata
from app.core.database import Base
from app.models.document import Chunk, Document
from app.models.notice import Notice
from app.repositories.documents import DocumentRepository
from app.repositories.notices import NoticeRepository


def _make_engine():
    return create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _new_session() -> Session:
    engine = _make_engine()
    Base.metadata.create_all(engine)
    return Session(engine)


def test_models_registered() -> None:
    tables = set(Base.metadata.tables)
    assert "documents" in tables
    assert "chunks" in tables
    assert "notices" in tables


def test_create_and_read_document() -> None:
    with _new_session() as session:
        repo = DocumentRepository(session)
        doc = Document(title="Admission Notice", source_url="https://amu.ac.in/notice/1")
        saved = repo.add(doc)
        assert saved.id is not None
        fetched = repo.get(saved.id)
        assert fetched is not None
        assert fetched.title == "Admission Notice"
        assert fetched.status == "active"
        assert repo.count() == 1


def test_document_with_chunks_and_count() -> None:
    with _new_session() as session:
        repo = DocumentRepository(session)
        doc = Document(title="Syllabus", source_url="https://amu.ac.in/syllabus.pdf")
        doc.chunks.append(Chunk(chunk_index=0, text="First section"))
        doc.chunks.append(Chunk(chunk_index=1, text="Second section", page_number=2))
        repo.add(doc)
        assert repo.count() == 1
        rows = repo.list_all()
        assert len(rows) == 1
        assert len(rows[0].chunks) == 2


def test_notice_repository() -> None:
    with _new_session() as session:
        repo = NoticeRepository(session)
        repo.add(Notice(title="Holiday", url="https://amu.ac.in/notice/2", category="general"))
        repo.add(Notice(title="Exam", url="https://amu.ac.in/notice/3", category="examinations"))
        recent = repo.list_recent(limit=10)
        assert len(recent) == 2
        assert repo.count() == 2
