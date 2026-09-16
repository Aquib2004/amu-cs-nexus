# AMUCS Nexus - Database Architecture

> TARGET DESIGN - not implemented yet.

## Storage boundaries

We do NOT put all data in one place. Storage has three roles:

| Store | Holds | Used for |
|-------|-------|----------|
| PostgreSQL | structured records, metadata, notices, faculty, courses, conversations, feedback, crawl jobs | authoritative, queryable application data |
| pgvector | document/chunk embeddings | semantic retrieval (vector similarity) |
| Object/file storage | PDFs, raw files, snapshots | original artifacts that are slow/expensive to store in a row |

PostgreSQL and pgvector live in the same database instance (pgvector is a PostgreSQL extension).

## Draft core tables

These are planned shapes to guide later phases; exact columns will be finalized with migrations (Phase 4).

### documents

| column | type | notes |
|--------|------|-------|
| document_id | uuid / serial PK | primary key |
| title | text | document title |
| source_url | text | where it came from |
| source_type | text | e.g. web, notice pdf, official pdf |
| document_type | text | e.g. notice, syllabus, paper |
| department | text | e.g. computer-science |
| publication_date | date | when published |
| updated_at | timestamptz | last updated |
| crawl_timestamp | timestamptz | when crawled |
| content_hash | text | deduplication / change detection |
| version | int | document version |
| status | text | draft/active/archived |

### chunks

| column | type | notes |
|--------|------|-------|
| chunk_id | uuid PK | primary key |
| document_id | FK -> documents | owning document |
| chunk_index | int | order within document |
| text | text | chunk content |
| page_number | int | for PDFs when available |
| embedding | vector | pgvector column |
| metadata | jsonb | flexible extra metadata |

### Other planned tables

- notices, faculty, courses, conversations, feedback, crawl_jobs (structured records reused by search and UI pages).

## Why PostgreSQL + pgvector instead of a separate vector database

- **One system to operate, back up, and deploy**, rather than two databases that must be kept consistent.
- **Atomic consistency** between a document and its embeddings (same transaction).
- **Simpler operations** for a modular monolith; fewer moving parts and less latency from network hops.
- A dedicated vector DB or Elasticsearch can be evaluated **later** only if measurements justify it (engineering decision policy).

## Data architecture principles

- Structured queries use PostgreSQL (dates, exact matches, filters).
- Semantic queries use pgvector. Hybrid search combines both.
- Raw files live in object/file storage; the database references them by URL or key, not as blobs.

