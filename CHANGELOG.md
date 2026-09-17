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
  - Input validation on `/api/search` (bounds on `q`, `limit`, filters) and `/api/chat`.
  - `scripts/seed_dev.py` for local sample data.
  - Documentation brought in line with the implemented functionality.
### Changed
- Backend, frontend, and AI READMEs now reflect implemented status.
### Fixed
- Backend no longer crashes on start with `ModuleNotFoundError: No module named ai`.
- Notices API return annotations corrected to `NoticeRead`.
### Not implemented
- Real LLM/embedding providers, running PostgreSQL/pgvector, scheduler, authentication, Docker/CI, Documents/Faculty/Research endpoints + UI.
