# AMUCS Nexus - Project Status

Project:
AMUCS Nexus

Current phase:
Phase 4 - Database layer (implemented and tested)

## Completed

- project root
- frontend structure
- backend structure
- ingestion structure
- database structure
- AI structure
- shared structure
- tests structure
- documentation structure
- infrastructure structure
- Git repository
- environment template
- open-source documentation skeleton

## Phase 1 - architecture documentation (committed)

- component diagram, data flows, sequence diagrams
- database architecture + storage boundaries
- API boundary + HTTP/REST primer
- ingestion flow, RAG flow
- ADR-001: modular monolith + PostgreSQL/pgvector

## Phase 0 - requirements (DRAFT, for review)

- product-requirements.md, functional-requirements.md, non-functional-requirements.md

## Phase 3 - backend foundation (implemented + tested)

- FastAPI wiring, settings, logging, global error handling, `/api/health`
- 4 API tests passing

## Phase 4 - database layer (implemented + tested)

- Engine/session/Base in `app/core/database.py` (PostgreSQL via DATABASE_URL, SQLite fallback for dev/tests).
- Models: Document, Chunk, Notice (`app/models/`).
- Repositories: DocumentRepository, NoticeRepository + BaseRepository (`app/repositories/`).
- Alembic migrations (`backend/alembic/`) with initial schema 0001.
- Tests validate models + repositories on in-memory SQLite: 4 tests passing. Alembic `upgrade head` verified to create all tables.

## Implemented to date

- backend health endpoint with configuration, logging, and error handling
- database models, repositories, and migrations

## Not implemented

- production UI
- REST business endpoints (notices, search, chat, documents, faculty, feedback)
- crawler
- PDF ingestion
- embeddings and pgvector column
- vector search
- RAG
- LLM integration
- PostgreSQL server running locally (deferred to containerization)
- LangChain / LangGraph / MCP
- authentication
- deployment

## Version roadmap

- V1: notices, documents, official pages, search, basic RAG, citations, chat.
- V2: faculty, research, courses, metadata filtering, hybrid search, reranking, scheduled ingestion, document versioning, evaluation dashboard.
- V3: LangGraph, tools, MCP, multi-step retrieval, advanced tool calling (only if justified).
