# Integration test: feed parsed content through the ingestion indexer into the
# database, using the backend SQLAlchemy models. Runs under the backend venv.

import importlib.util
from pathlib import Path

import app.models  # noqa: F401
from app.core.database import Base
from app.models.document import Chunk, Document
from app.repositories.documents import DocumentRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

# Load the ingestion indexer module by path (it has no intra-ingestion imports,
# so it works here where the backend `app` package is on sys.path).
INGESTION_INDEXER = (
    Path(__file__).resolve().parents[2] / "ingestion" / "app" / "indexer.py"
)
_spec = importlib.util.spec_from_file_location("ingestion_indexer", INGESTION_INDEXER)
_indexer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_indexer)


def _session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Session(engine)


def test_index_document_persists_document_and_chunks() -> None:
    with _session() as session:
        doc = Document(
            title="Exam Schedule",
            source_url="https://amu.ac.in/exam",
            document_type="web_page",
        )
        doc.chunks.append(Chunk(chunk_index=0, text="Mid-semester exams start on 1 October."))
        _indexer.index_document(session, doc)

        repo = DocumentRepository(session)
        assert repo.count() == 1
        rows = repo.list_all()
        assert rows[0].title == "Exam Schedule"
        assert len(rows[0].chunks) == 1
