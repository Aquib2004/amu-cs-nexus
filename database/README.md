# AMUCS Nexus - Database

Database management assets for AMUCS Nexus. Nothing is implemented yet.

## Storage design

Separate storage responsibilities, rather than putting all data into one place:

### PostgreSQL
- Structured records and metadata: notices, documents, faculty, courses, conversations, feedback, crawl jobs.

### pgvector (PostgreSQL extension)
- Document/chunk embeddings and semantic retrieval. pgvector is used instead of a separate vector database at this stage.

### File/object storage (future)
- PDFs, raw files, snapshots when required.

## Why PostgreSQL + pgvector, not a separate vector DB

PostgreSQL already stores the structured data. pgvector adds vector columns and ANN index support inside the same database, so we get:

- One database to operate, back up, and deploy, instead of multiple.
- Atomic consistency between a document's metadata and its embeddings.
- Simpler operations and less moving infrastructure for a modular monolith.

A dedicated vector database (Pinecone, Qdrant, Weaviate) or Elasticsearch can be evaluated later **if measurements show it is necessary**. It is not added prematurely (per the engineering decision policy).

## Directory layout

- `migrations` - SQLAlchemy/Alembic migrations (future).
- `schemas` - initial SQL / data definitions (future).
- `seeds` - seed data for development (future).
- `scripts` - database helper scripts (future).
