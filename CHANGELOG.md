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
- Backend foundation (Phase 3): FastAPI wiring, settings, logging, error handling, tested `/api/health`.
- Database layer (Phase 4): SQLAlchemy models (`Document`, `Chunk`, `Notice`), repositories, and an Alembic initial migration. Validated with in-memory SQLite tests.

### Not yet implemented

- Production UI, business REST endpoints (notices/search/chat), crawler, ingestion pipeline, embeddings/pgvector, vector search, RAG, LLM integration, running PostgreSQL server, authentication, deployment.
