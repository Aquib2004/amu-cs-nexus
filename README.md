# AMUCS Nexus

An open-source knowledge, search, document retrieval, and AI information platform for the Department of Computer Science, Aligarh Muslim University (AMU).

AMUCS Nexus is NOT simply an AI chatbot. It is a domain-specific information retrieval platform that helps students and users find and understand publicly available official information about the AMU Department of Computer Science: notices, admissions, academics, courses, faculty, research, documents, and more.

The central principle:

> AMUCS Nexus provides verifiable, source-grounded information rather than confident but unsupported answers.

## Current status

- Backend (FastAPI): health, notices, search, source-grounded chat, directory, exam, upload, and notification endpoints. SQLAlchemy models and Alembic migration 0005 are applied to the development SQLite database.
- AI layer: `ai/retrieval`, `ai/rag`, Gemini and Groq providers, Gemini `gemini-embedding-2` vectors, structured intent routing, citation validation/repair, and an extractive fallback that never invents URLs, dates, or exam information.
- Ingestion: live AMU department API and official Controller of Examinations ingestion, with idempotent upserts and `ingestion_log` auditing.
- Frontend (Next.js): YouRobo with official/private-file modes, per-answer citations, file selection for PDF/DOCX/TXT/Markdown, and an explicit opt-in notice-alert control.
- See `docs/development/project-status.md` for precise status and `CHANGELOG.md` for changes.

### Privacy and deployment notes
- Uploaded files are processed in memory; the original binary is discarded. Only extracted text, chunks, metadata, and a SHA-256 hash of a one-time access token are stored. Uploads expire after 24 hours by default and require the token for every question.
- Notice notifications are anonymous and opt-in. Browser permission is requested only after the student presses **Enable alerts**. VAPID private keys belong in the untracked `backend/.env`; never commit them.

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
