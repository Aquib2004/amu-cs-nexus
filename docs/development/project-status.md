# AMUCS Nexus - Project Status

Current phase: Phase 9 - Retrieval (implemented and tested)

Completed: Phases 1-8 (see prior entries). Phase 9 adds retrieval.

## Phase 9 - retrieval (implemented + tested)
- `ai/retrieval/`: pure algorithms - scoring (cosine, reciprocal-rank fusion), keyword, semantic, hybrid.
- Backend `app/services/search.py` + `api/search.py`: GET /api/search?q=&limit=&department=&document_type= with metadata filters.
- Frontend `/search` page + `src/services/search.ts`; Header links to Search.
- Tests: ai retrieval 5 pass; backend 16 pass (incl. search API on seeded SQLite). Live HTTP demo verified (q=vision -> source; q=no-match -> []).
- Real pgvector `<=>` and production embeddings still need a running PostgreSQL server + provider credentials.

Not implemented: Chat/Documents/Faculty/Research endpoints+UI, RAG (Phase 10), LLM, scheduler, running PostgreSQL server, LangChain/LangGraph/MCP, auth, deployment.
