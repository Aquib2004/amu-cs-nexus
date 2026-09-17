# AMUCS Nexus - Project Status

Current phase: Phase 8 - Embeddings (implemented; pgvector needs Postgres)

Completed: monorepo, env template, open-source docs, git (GitHub). Phases 1 (architecture+ADR-001), 0 (requirements draft), 3 (backend foundation), 4 (database models/repos/migrations+SQLite tests), 5 (frontend foundation), 6 (API integration: /api/notices + Notices page), 7 (ingestion pipeline: discover/crawl/parse/clean/metadata/chunk/index).

## Phase 8 - embeddings (implemented + tested)
- `ai`/ingestion `embedder.py`: Embedder interface, deterministic offline `HashEmbedder`, `ProviderEmbedder` stub.
- Portable `VectorType` column: pgvector.vector on PostgreSQL, CSV text on SQLite for offline tests.
- `Chunk.embedding` column + Alembic migration 0002 (verified: upgrade head -> 0002, column present).
- Tests: ingestion 13 pass, backend 13 pass (incl. embedding round-trip on SQLite).
- Real pgvector execution still requires a running PostgreSQL server (containerization, Phase 14).

Not implemented: Search/Chat/Documents/Faculty/Research endpoints+UI, retrieval (Phase 9), RAG, LLM, scheduler, running PostgreSQL server, LangChain/LangGraph/MCP, auth, deployment.
