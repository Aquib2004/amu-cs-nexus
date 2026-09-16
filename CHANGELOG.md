# Changelog

All notable changes to this project are documented in this file.

The format is inspired by Keep a Changelog, with versioning following semantic versioning (MAJOR.MINOR.PATCH).

## [Unreleased]

### Added

- Monorepo skeleton, env template, `.gitignore`, open-source docs skeleton.
- Phase 1 architecture docs and ADR-001.
- Phase 0 requirements (draft).
- Phase 3 backend foundation: config, logging, error handling, `/api/health`.
- Phase 4 database: SQLAlchemy models, repositories, Alembic migration, SQLite tests.
- Phase 5 frontend foundation: Next.js layout, typed API client, health service, home page.
- Phase 6 API integration: `GET /api/notices` and `GET /api/notices/{id}` on the backend; `/notices` page on the frontend; API tests; live end-to-end verified.

### Not yet implemented

- Search, Chat, Documents, Faculty, Research UI + endpoints, frontend tests, crawler, ingestion, embeddings/pgvector, vector search, RAG, LLM integration, running PostgreSQL server, authentication, deployment.
