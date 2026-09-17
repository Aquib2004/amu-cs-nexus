# AMUCS Nexus

An open-source knowledge, search, document retrieval, and AI information platform for the Department of Computer Science, Aligarh Muslim University (AMU).

AMUCS Nexus is NOT simply an AI chatbot. It is a domain-specific information retrieval platform that helps students and users find and understand publicly available official information about the AMU Department of Computer Science: notices, admissions, academics, courses, faculty, research, documents, and more.

The central principle:

> AMUCS Nexus provides verifiable, source-grounded information rather than confident but unsupported answers.

## Current status

- Backend (FastAPI): health, notices, search (keyword + semantic + hybrid), and source-grounded chat (RAG) endpoints. SQLAlchemy models + Alembic migrations. CORS and input validation in place.
- AI layer: `ai/retrieval` (cosine, reciprocal-rank fusion, keyword, semantic, hybrid) and `ai/rag` (evidence, citations, extractive generator). `POST /api/chat` answers from retrieved evidence with cited sources; it does not require an LLM and cannot fabricate claims.
- Ingestion: crawler, HTML/PDF parsing, cleaning, metadata, chunking, indexer - implemented and unit-tested with sample content. No live AMU crawling is performed.
- Frontend (Next.js): Home, Search, Notices, Chat pages wired to the API. Documents, Faculty, Research are placeholders.
- See `docs/development/project-status.md` for precise status and `CHANGELOG.md` for changes.

### Not implemented (honest)
Real LLM/embedding providers (requires credentials), running PostgreSQL/pgvector (dev uses SQLite), scheduler, authentication, Docker/CI deployment, Documents/Faculty/Research endpoints
+UI. A dedicated chatbot with an LLM is not wired. Powers `POST /api/chat` uses the offline, extractive RAG path.

## Repository structure

```text
amu-cs-nexus/
|-- frontend/    presentation and client-side UX (Next.js)
|-- backend/     FastAPI REST API and application logic
|-- ingestion/   acquiring and processing official source material
|-- database/    database management assets
|-- ai/          retrieval, RAG, embeddings, orchestration
|-- shared/      shared contracts
|-- tests/       project-wide testing
|-- docs/        engineering documentation
|-- infra/       deployment/infrastructure
|-- scripts/     helper scripts (seed_dev.py)
`-- .github/     CI workflows (placeholder)
```

## Requirements

- Python 3.10+ (backend/ingestion/ai)
- Node.js 18+ (frontend)
- No running database required for local dev (SQLite default); PostgreSQL recommended for production.

## Run locally (verified)

Backend (from `backend/`):
```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python ..\scripts\seed_dev.py      # optional sample data
.venv\Scripts\python -m uvicorn app.main:app --reload
```

Frontend (from `frontend/`):
```bash
npm install
npm run dev
```

Open http://localhost:3000. API docs: http://localhost:8000/docs.

## Tests

```bash
cd backend; .venv\Scripts\python -m pytest -q
cd ai;      backend\.venv\Scripts\python -m pytest tests -q
cd ingestion; .venv\Scripts\python -m pytest tests -q
cd frontend; npx tsc --noEmit
```

## Open-source status

Repository designed for public collaboration. License decision pending (see `LICENSE`); contribution guidance in `CONTRIBUTING.md`; code of conduct in `CODE_OF_CONDUCT.md`. Never commit API keys, passwords, or private credentials.

## Documentation

- `docs/architecture/system-overview.md` - system architecture.
- `docs/development/project-status.md` - current project status.
- `docs/requirements/` - product/functional/non-functional requirements.
- `backend/README.md`, `frontend/README.md`, `ingestion/README.md`, `ai/README.md` - per-component guides.
