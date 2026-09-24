# scripts/ingest_real.py - make the database "real":
#   1) remove all fabricated sample rows (seed docs, fake faculty, fake notices)
#   2) run live AMU ingestion (real data + real embeddings when a key is set)
#
# Run from the backend/ directory:
#   .\.venv\Scripts\python.exe ..\scripts\ingest_real.py

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # amu-cs-nexus/
BACKEND = ROOT / "backend"
for _p in (str(ROOT), str(BACKEND)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sqlalchemy as sa  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.models.document import Chunk, Document  # noqa: E402
from app.models.faculty import Faculty  # noqa: E402
from app.models.notice import Notice  # noqa: E402

logger = logging.getLogger("ingest_real")

# Placeholder names from the old seed script - delete so only real AMU staff remain.
PLACEHOLDER_NAMES = ["Prof. A. Rahman", "Dr. S. Begum", "Dr. M. Fahad", "Ms. N. Aziz"]


def clear_sample_data() -> None:
    session = SessionLocal()
    try:
        # Seed documents never had content hashes; real ingestion always sets them.
        seed_ids = session.execute(
            sa.select(Document.id).where(Document.content_hash.is_(None))
        ).scalars().all()
        deleted_chunks = 0
        for doc_id in seed_ids:
            deleted_chunks += session.query(Chunk).filter(Chunk.document_id == doc_id).delete(
                synchronize_session=False
            )
        deleted_docs = len(seed_ids)
        if seed_ids:
            session.query(Document).filter(Document.id.in_(seed_ids)).delete(
                synchronize_session=False
            )
        deleted_notices = session.query(Notice).delete()
        removed_faculty = 0
        for name in PLACEHOLDER_NAMES:
            removed_faculty += session.query(Faculty).filter(Faculty.name == name).delete(
                synchronize_session=False
            )
        session.commit()
        logger.info("cleaned seed data: chunks=%d documents=%d notices=%d placeholder_faculty=%d",
                    deleted_chunks, deleted_docs, deleted_notices, removed_faculty)
    finally:
        session.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    clear_sample_data()

    # Load the ingestion module by path (the top-level `ingestion` dir is not a package).
    import importlib.util

    module_path = ROOT / "ingestion" / "app" / "amu_ingest.py"
    spec = importlib.util.spec_from_file_location("amu_ingest", module_path)
    amu = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(amu)

    total = amu.run_ingestion(embedding=True)
    logger.info("done. total rows written: %d", total)


if __name__ == "__main__":
    main()