# AMUCS Nexus - Project Status

Project:
AMUCS Nexus

Current phase:
Phase 0 - Requirements (draft) + Phase 1 - Architecture docs

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

## Phase 1 - architecture documentation

- component diagram (`docs/architecture/component-diagram.md`)
- data flows (`docs/architecture/data-flow.md`)
- sequence diagrams (`docs/architecture/sequence-diagrams.md`)
- database architecture + storage boundaries (`docs/database/database-architecture.md`)
- API boundary + HTTP/REST primer (`docs/api/api-boundary.md`)
- ingestion flow (`docs/ingestion/ingestion-flow.md`)
- RAG flow (`docs/rag/rag-flow.md`)
- decision record: modular monolith + PostgreSQL/pgvector (`docs/decisions/ADR-001-modular-monolith-postgres-pgvector.md`)

## Phase 0 - requirements (DRAFT, for review)

- product requirements (`docs/requirements/product-requirements.md`)
- functional requirements (`docs/requirements/functional-requirements.md`)
- non-functional requirements (`docs/requirements/non-functional-requirements.md`)

## Implemented (minimal)

- backend health endpoint skeleton (`GET /api/health`)

## Not implemented

- production UI
- REST business endpoints
- crawler
- PDF ingestion
- embeddings
- vector search
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
