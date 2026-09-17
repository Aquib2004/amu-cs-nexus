# Changelog

All notable changes to this project are documented in this file.

The format is inspired by Keep a Changelog, with versioning following semantic versioning (MAJOR.MINOR.PATCH).

## [Unreleased]

### Added

- Monorepo skeleton, env template, `.gitignore`, open-source docs skeleton.
- Phase 1 architecture docs and ADR-001.
- Phase 0 requirements (draft).
- Phase 3 backend foundation.
- Phase 4 database (models, repositories, migrations, SQLite tests).
- Phase 5 frontend foundation.
- Phase 6 API integration (`/api/notices` + Notices page).
- Phase 7 ingestion pipeline: URL discovery, crawler, HTML/PDF parsing, cleaner, metadata, chunker, indexer; unit tests on sample/local content plus a backend integration test.

### Not yet implemented

- Embeddings/pgvector, Search/Chat/Documents/Faculty/Research UI + endpoints, ingestion scheduler, RAG, LLM, running PostgreSQL server, auth, deployment.
