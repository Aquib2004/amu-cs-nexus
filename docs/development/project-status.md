# AMUCS Nexus - Project Status

Project:
AMUCS Nexus

Current phase:
Phase 6 - API integration (implemented and tested)

## Completed

- project root and full monorepo structure
- environment template and open-source documentation skeleton
- Git repository (on GitHub)

## Phase 1 - architecture documentation (committed)

- component diagram, data flows, sequence diagrams, database architecture, API boundary, ingestion flow, RAG flow
- ADR-001: modular monolith + PostgreSQL/pgvector

## Phase 0 - requirements (DRAFT)

- product-requirements.md, functional-requirements.md, non-functional-requirements.md

## Phase 3 / 4 - backend + database (implemented + tested)

- FastAPI foundation, `/api/health`, settings, logging, error handling
- SQLAlchemy models (Document, Chunk, Notice), repositories, Alembic migration 0001
- PostgreSQL via DATABASE_URL; SQLite fallback for dev/tests

## Phase 5 - frontend foundation (implemented)

- Next.js layout, typed API client, health service, home page
- TypeScript type-check verified. Full `next build` blocked in this env by corrupted Next SWC binary (resolves with clean `npm install`).

## Phase 6 - API integration (implemented + tested)

- Backend: `GET /api/notices` and `GET /api/notices/{id}` (Pydantic schema + NoticeRepository + get_db dependency).
- Frontend: `/notices` page calls the API and renders notices; Header links to it.
- 3 new API tests (list, get, 404). Live end-to-end verified over HTTP from the PostgreSQL-target SQLite dev DB.

## Implemented to date

- backend health endpoint, database models/repositories/migrations, notices API + frontend notices page

## Not implemented

- Search, Chat, Documents, Faculty, Research UI + endpoints
- frontend tests
- crawler
- PDF ingestion
- embeddings and pgvector column
- vector search
- RAG
- LLM integration
- running PostgreSQL server (deferred to containerization)
- LangChain / LangGraph / MCP
- authentication
- deployment

## Version roadmap

- V1: notices, documents, official pages, search, basic RAG, citations, chat.
- V2: faculty, research, courses, metadata filtering, hybrid search, reranking, scheduled ingestion, document versioning, evaluation dashboard.
- V3: LangGraph, tools, MCP, multi-step retrieval, advanced tool calling (only if justified).
