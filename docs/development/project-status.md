# AMUCS Nexus - Project Status

Current phase: Phase 10 (RAG / grounded chat) + release hardening.

## Implemented (verified)

- Backend (FastAPI): GET /api/health, GET /api/notices, GET /api/notices/{id}, GET /api/search (hybrid + filters), POST /api/chat (grounded answer + sources). CORS, input validation, logging, error handling.
- Database: SQLAlchemy models (Document, Chunk, Notice), Alembic migrations 0001/0002. Dev DB is SQLite; PostgreSQL is the production target.
- Ingestion: crawler, HTML/PDF parser, cleaner, metadata, chunker, indexer (Phase 7); deterministic dev embedder + embedding column (Phase 8). Tests use sample content only; no live AMU crawling.
- AI: ai/retrieval (cosine, reciprocal-rank fusion, keyword, semantic, hybrid) and ai/rag (evidence, citations, extractive answerer).
- Frontend (Next.js + TS): Home, Search, Notices, Chat pages wired to the API.

## Verified by tests

- backend: 19 pass; ai: 10 pass; ingestion: 13 pass; frontend `tsc --noEmit`: 0 errors.
- Live HTTP checks: /api/health 200; /api/search returns seeded source-grounded result; /api/chat returns a cited answer; invalid query (limit=999) -> 422; CORS preflight returns allow-origin.

## Known limitations

- Dev uses SQLite (`amucs_nexus_dev.db`); real pgvector `<=>` and provider embeddings require a running PostgreSQL server with the pgvector extension and provider credentials.
- No LLM provider wired; /api/chat uses the offline extractive RAG path (cannot fabricate claims).
- No authentication, scheduler, Docker/CI deployment, or production hosting.
- `next build` requires a clean, complete `npm install` (Next.js SWC).

## Not implemented

Documents/Faculty/Research endpoints + UI, feedback endpoint, scheduler, Real LLM/embeddings provider integration, auth, deployment, LangChain/LangGraph/MCP.
