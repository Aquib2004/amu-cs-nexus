# Changelog

All notable changes are documented here. Format based on Keep a Changelog; versioning follows Semantic Versioning (yet to be formally released).

## [Unreleased]

### Added
- Phases 1-9: monorepo init, architecture/requirements docs, backend foundation, database layer, frontend foundation, API integration (notices/search), ingestion pipeline, embeddings field, retrieval search.
- Phase 10 (RAG) + release fixes:
  - `ai/rag` (evidence, citations, extractive generator) and `ai/prompts` (system prompt templates).
  - `POST /api/chat`: source-grounded answer + cited sources via retrieval + extractive RAG.
  - Frontend `/chat` page + chat service.
  - Backend boot fix: repository-root `ai` package now importable outside pytest (bootstrap).
  - CORS middleware (configurable via `CORS_ORIGINS`).
  - Input validation on `/api/search` and `/api/chat`.
  - `scripts/seed_dev.py` for local sample data.
- Documents / Faculty / Research + Exams:
  - Backend: `GET /api/documents`, `GET /api/documents/{id}`, `GET /api/faculty`, `GET /api/research` (models, schemas, repositories, routers, migration 0003, directory API tests).
  - Frontend: `/documents`, `/faculty`, `/research`, `/exams` pages wired to the API and linked in the header.
- YouRobo (Gemini) chatbot:
  - `ai/providers/gemini.py`: Gemini `generateContent` client with bounded retries and typed error mapping; API key sent in a header, never in the URL.
  - `LLM_PROVIDER=gemini` + `LLM_API_KEY` (or `GEMINI_API_KEY` alias) enables the real provider; without a key chat degrades to the offline extractive answerer by design.
  - Frontend `/chat` page rebranded as "YouRobo" (logo, chat bubbles, suggestion chips, provider badge, collapsible sources, notice banner).
- UI redesign: AMU logo in header + favicon, modern stylesheet (hero, card grid, badges, responsive layout, focus-visible states, consistent empty/error/loading states).
- `scripts/seed_dev.py` enriched (5 dev documents + 4 sample faculty; idempotent per record).
- Docs: `docs/decisions/ADR-002-branding-and-logo.md`, developer guide section on YouRobo/Gemini, `.env.example` documents `GEMINI_API_KEY` alias and `LLM_MODEL`.

### Changed
- Backend, frontend, and AI READMEs now reflect implemented status.
- `AMUCS Nexus` brand retained; assistant persona named "YouRobo".

### Fixed
- Backend no longer crashes on start with `ModuleNotFoundError: No module named ai`.
- Notices API return annotations corrected to `NoticeRead`.
- Frontend dev/build blockers (corrupt SWC binary, BOM in files, broken home-directory postcss config).

### Not implemented
- Real embeddings + running PostgreSQL/pgvector, scheduler, authentication, Docker/CI deployment, feedback endpoint, LangChain/LangGraph/MCP.