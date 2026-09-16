# AMUCS Nexus - Project Status

Project:
AMUCS Nexus

Current phase:
Phase 3 - Backend Foundation (implemented and tested)

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

- FastAPI application wiring in `app/main.py` (config, logging, error handling, routers).
- Settings via pydantic-settings (`app/core/config.py`).
- Logging setup (`app/core/logging.py`).
- Global exception handlers + `AppError` (`app/core/errors.py`).
- `/api/health` returns status + application identity.
- API tests in `backend/tests/test_health.py` - 4 passing.
- Isolated venv at `backend/.venv`; deps in `requirements.txt` + `requirements-dev.txt`.

## Implemented to date

- backend health endpoint with configuration, logging, and error handling

## Not implemented

- production UI
- REST business endpoints (notices, search, chat, documents, faculty, feedback)
- crawler
- PDF ingestion
- embeddings
- vector search
- database models / migrations
- RAG
- LLM integration
- LangChain
- LangGraph
- MCP
- authentication
- deployment

## Version roadmap

- V1: notices, documents, official pages, search, basic RAG, citations, chat.
- V2: faculty, research, courses, metadata filtering, hybrid search, reranking, scheduled ingestion, document versioning, evaluation dashboard.
- V3: LangGraph, tools, MCP, multi-step retrieval, advanced tool calling (only if justified).
