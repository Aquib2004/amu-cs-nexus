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
- Backend foundation (Phase 3): config, logging, error handling, tested `/api/health`.
- Database layer (Phase 4): SQLAlchemy models, repositories, Alembic migration, SQLite-backed tests.
- Frontend foundation (Phase 5): Next.js layout, typed API client, health service, home page; `package-lock.json`.

### Not yet implemented

- Production UI for Chat/Search/Notices/Documents/Faculty/Research, backend business endpoints, frontend tests, crawler, ingestion, embeddings/pgvector, vector search, RAG, LLM integration, running PostgreSQL server, authentication, deployment.
