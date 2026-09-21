# AMUCS Nexus - Project Status

Current phase: Phase 10 (RAG / grounded chat) + release hardening + YouRobo assistant.

## Implemented (verified)

- Backend (FastAPI): GET /api/health, GET /api/notices, GET /api/notices/{id}, GET /api/search (hybrid + filters), POST /api/chat (grounded answer + sources), GET /api/documents, GET /api/documents/{id}, GET /api/faculty, GET /api/research. CORS, input validation, logging, error handling.
- Database: SQLAlchemy models (Document, Chunk, Notice, Faculty), Alembic migrations 0001/0002/0003. Dev DB is SQLite; PostgreSQL is the production target.
- Ingestion: crawler, HTML/PDF parser, cleaner, metadata, chunker, indexer (Phase 7); deterministic dev embedder + embedding column (Phase 8). Tests use sample content only; no live AMU crawling.
- AI: ai/retrieval (cosine, reciprocal-rank fusion, keyword, semantic, hybrid) and ai/rag (evidence, citations, extractive answerer).
- AI provider: ai/providers/gemini.py (Gemini client with retries + typed errors). Enabled via LLM_PROVIDER=gemini + LLM_API_KEY (or GEMINI_API_KEY alias). Falls back to extractive when no key.
- Frontend (Next.js + TS): Home, Search, Notices, Chat (YouRobo), Documents, Faculty, Research, Exams pages wired to the API. AMU logo in header/favicon.

## Verified by tests

- backend: 23 pass; ai: 12 pass; ingestion: 13 pass; frontend `tsc --noEmit`: 0 errors.
- Live HTTP checks: /api/health 200; /api/search returns seeded source-grounded result; /api/chat returns a cited answer; /api/documents and /api/faculty return seeded rows (5 documents, 4 faculty) with source information; invalid limit -> 422; CORS preflight returns allow-origin.

## Known limitations

- Dev uses SQLite (`amucs_nexus_dev.db`); real pgvector `<=>` and provider embeddings require a running PostgreSQL server with the pgvector extension and provider credentials.
- LLM key is optional and not shipped; /api/chat uses the offline extractive RAG path when no key is configured (cannot fabricate claims).
- Sample faculty/document rows are clearly-labelled development data, not the official staff list.
- No authentication, scheduler, Docker/CI deployment, or production hosting.
- `next build` requires a clean, complete `npm install` (Next.js SWC).

## Not implemented

Faculty/document ingestion from the live AMU site, feedback endpoint, real pgvector execution, scheduler, auth, deployment, LangChain/LangGraph/MCP.