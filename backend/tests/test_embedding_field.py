# Chunk embedding round-trip on SQLite (portable vector type).

import app.models  # noqa: F401
from app.core.database import Base
from app.models.document import Chunk, Document
from app.repositories.documents import DocumentRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


def _session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Session(engine)


def test_chunk_embedding_round_trip() -> None:
    with _session() as session:
        repo = DocumentRepository(session)
        doc = Document(title="T", source_url="https://amu.ac.in/t")
        doc.chunks.append(Chunk(chunk_index=0, text="hello", embedding=[0.1, 0.2, 0.3]))
        repo.add(doc)
        rows = repo.list_all()
        assert rows[0].chunks[0].embedding == [0.1, 0.2, 0.3]
