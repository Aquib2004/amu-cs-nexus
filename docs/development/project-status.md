# AMUCS Nexus - Project Status

Project:
AMUCS Nexus

Current phase:
Phase 5 - Frontend foundation (implemented; type-check verified)

## Completed

- project root and full monorepo structure
- environment template and open-source documentation skeleton
- Git repository (on GitHub)

## Phase 1 - architecture documentation (committed)

- component diagram, data flows, sequence diagrams
- database architecture + storage boundaries, API boundary, ingestion flow, RAG flow
- ADR-001: modular monolith + PostgreSQL/pgvector

## Phase 0 - requirements (DRAFT)

- product-requirements.md, functional-requirements.md, non-functional-requirements.md

## Phase 3 - backend foundation (implemented + tested)

- FastAPI wiring, settings, logging, error handling, `/api/health`
- 4 API tests passing

## Phase 4 - database layer (implemented + tested)

- SQLAlchemy models (Document, Chunk, Notice), repositories, Alembic migration 0001
- 4 database tests passing; `alembic upgrade head` verified

## Phase 5 - frontend foundation (implemented)

- Next.js (App Router) layout with header/nav/footer
- Typed API client and health service (`src/lib/api.ts`, `src/services/health.ts`)
- Types (`src/types`) and a home page that live-fetches backend `/api/health`
- TypeScript type-check passes (`tsc --noEmit`). Full `next build` blocked by a corrupted Next.js native compiler (SWC) left by an interrupted `npm install` in this environment - not a code issue. Resolve locally with a clean `npm install`.

## Implemented to date

- backend health endpoint with config, logging, error handling
- database models, repositories, migrations
- frontend foundation (layout + typed API client + health page)

## Not implemented

- production UI for Chat/Search/Notices/Documents/Faculty/Research
- backend business endpoints (notices, search, chat, documents, faculty, feedback)
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
