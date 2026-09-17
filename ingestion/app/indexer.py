# Indexer: persist parsed documents (and their chunks) to the database.
#
# In production, ingestion and the backend share one database. Ingestion
# runs as a separate process, so this module avoids direct imports of the
# backend `app` package; callers construct the backend ORM objects (Document,
# Chunk) and pass them here. DB persistence itself is validated by the
# backend database tests (Phase 4).

def index_document(session, document) -> None:
    """Persist a Document (with its chunks) and commit the transaction."""
    session.add(document)
    session.commit()
