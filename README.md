# AMUCS Nexus

An open-source knowledge, search, document retrieval, and AI information platform for the Department of Computer Science, Aligarh Muslim University (AMU).

AMUCS Nexus is NOT simply an AI chatbot. It is a domain-specific information retrieval platform that helps students and users find and understand publicly available official information about the AMU Department of Computer Science: notices, admissions, academics, courses, faculty, research, documents, and more.

The central principle:

> AMUCS Nexus provides verifiable, source-grounded information rather than confident but unsupported answers.

## Project Goals

- Provide searchable access to official, publicly available AMU Department of Computer Science information.
- Support multiple access patterns: website search, document search, semantic search, hybrid search, and conversational question answering.
- Ground every AI answer in retrieved evidence with citations and source links.
- Keep the AI as one component of a larger platform, not the entire product.
- Prefer "I could not verify this from the indexed official sources." over hallucination.

## Current Project Status

Repository initialization. The project structure, open-source documentation skeleton, environment template, and a single Git repository exist. No production UI, crawler, ingestion pipeline, vector search, RAG, or LLM integration has been built yet. See `docs/development/project-status.md` for the precise status.

## Initial Architecture

A modular monolith with separate logical subsystems:

- `frontend` - React / Next.js presentation layer.
- `backend` - FastAPI REST API and application logic.
- `ingestion` - acquiring and processing official source material.
- `database` - PostgreSQL + pgvector assets (migrations, schemas).
- `ai` - LLM, embeddings, retrieval, RAG, orchestration, evaluation.
- `shared` - shared contracts used by multiple subsystems.
- `infra` - deployment and infrastructure assets.

Target architecture and data flows are documented in `docs/architecture/system-overview.md`. That document is marked as TARGET ARCHITECTURE; not all components are implemented yet.

## Repository Structure

```text
amu-cs-nexus/
|-- frontend/    presentation and client-side UX
|-- backend/     API and application logic
|-- ingestion/   acquiring and processing source material
|-- database/    database management assets
|-- ai/          LLM, embeddings, retrieval, RAG, orchestration
|-- shared/      shared contracts
|-- tests/       project-wide testing
|-- docs/        engineering documentation
|-- infra/       deployment/infrastructure
`-- scripts/     project helper scripts
```

## Technology Direction

- Frontend: React + TypeScript, likely Next.js.
- Backend: Python + FastAPI.
- Database: PostgreSQL, with pgvector for vector search when embeddings are built.
- AI: provider-agnostic LLM, embeddings, retrieval and RAG layers.

No LangChain, LangGraph, MCP, Redis, Kafka, Celery, Kubernetes, microservices, or a dedicated vector database are introduced prematurely. Technologies are added only when an actual engineering requirement appears.

## Open-Source Status

The repository is designed for public collaboration. A license decision is pending (see `LICENSE`). Contribution guidance is in `CONTRIBUTING.md`, and the code of conduct in `CODE_OF_CONDUCT.md`. Never commit API keys, passwords, or private credentials.

## Development Philosophy

1. Build incrementally: understand, design, create structure, implement, test, document, review, extend.
2. Understand what is built before building more.
3. Favor simple, maintainable solutions over over-engineering.
4. Measure before optimizing.
5. Never claim a feature works until it is implemented and tested.

## Setup

Setup instructions will be documented as implementation progresses (Phase 2 onwards). Nothing is runnable yet beyond the repository skeleton.

## Documentation

- `docs/architecture/system-overview.md` - target system architecture.
- `docs/development/project-status.md` - current project status.
- `docs/requirements/` - product requirements (created when Phase 0 begins).

