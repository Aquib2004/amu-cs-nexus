# Changelog

All notable changes to this project are documented in this file.

The format is inspired by Keep a Changelog, with versioning following semantic versioning (MAJOR.MINOR.PATCH).

## [Unreleased]

### Added

- Monorepo skeleton: frontend, backend, ingestion, database, ai, shared, tests, docs, infra.
- Environment template (`.env.example`) and `.gitignore`.
- Open-source documentation skeleton: LICENSE (pending), CONTRIBUTING, CODE_OF_CONDUCT, SECURITY.
- Phase 1 architecture docs and ADR-001.
- Phase 0 requirements (draft).
- Backend foundation (Phase 3): FastAPI wiring, settings (pydantic-settings), logging, global error handling with `AppError`, and a tested `/api/health` endpoint. Backend dependencies and dev deps in `requirements.txt` / `requirements-dev.txt`.

### Not yet implemented

- Production UI, business REST endpoints (notices/search/chat), crawler, ingestion pipeline, embeddings, vector search, database models/migrations, RAG, LLM integration, authentication, deployment.
