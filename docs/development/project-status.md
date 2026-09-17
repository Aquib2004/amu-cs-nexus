# AMUCS Nexus - Project Status

Project:
AMUCS Nexus

Current phase:
Phase 7 - Ingestion pipeline (implemented and tested)

## Completed

- project root and full monorepo structure
- environment template and open-source documentation skeleton
- Git repository (on GitHub)

## Phase 1 - architecture documentation
- component diagram, data flows, sequence diagrams, database architecture, API boundary, ingestion flow, RAG flow
- ADR-001: modular monolith + PostgreSQL/pgvector

## Phase 0 - requirements (DRAFT)
- product / functional / non-functional requirements

## Phase 3 / 4 - backend + database
- FastAPI foundation, `/api/health`, settings, logging, error handling
- SQLAlchemy models, repositories, Alembic migration, SQLite tests

## Phase 5 / 6 - frontend + API integration
- Next.js layout, typed API clients, health + notices pages
- `/api/notices` endpoints; live end-to-end verified

## Phase 7 - ingestion pipeline (implemented + tested)
- URL discovery, crawler (fetch HTML), HTML parser, PDF parser, cleaner, metadata, chunker, indexer
- 9 unit tests (processing + crawler/pdf) on sample/local content; no live AMU crawling
- Backend integration test proves the indexer persists Document + chunks

## Implemented to date
- backend health + notices endpoints; database models/repositories/migrations; frontend foundation + notices page; ingestion processing pipeline + indexer

## Not implemented
- Embeddings and pgvector column (Phase 8)
- Search, Chat, Documents, Faculty, Research UI + endpoints
- Ingestion scheduler / scheduled runs
- frontend tests
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
