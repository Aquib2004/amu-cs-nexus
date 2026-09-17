# AMUCS Nexus - Backend

Python + FastAPI REST API and application logic for AMUCS Nexus.

> STATUS: Implemented - health, notices, search, and grounded chat (RAG) endpoints, SQLAlchemy models (Document/Chunk/Notice), a migrations setup, and a database layer. Logging and error handling are wired. No authentication is configured yet (by design).

## Endpoints

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET  | /api/health        | Service status + identity | - |
| GET  | /api/notices       | List notices (limit/offset) | - |
| GET  | /api/notices/{id}  | Single notice or 404 | - |
| GET  | /api/search        | Hybrid search with filters (q, limit, department, document_type) | - |
| POST | /api/chat          | Source-grounded answer + cited sources (RAG) | - |

Interactive API docs are served by FastAPI at `/docs` when running.

## Important: importing the `ai` package

The backend imports the shared `ai` package (retrieval/RAG), which lives at the repository root, not inside `backend/`. `app/__init__.py` runs a bootstrap that puts the repo root on `sys.path`, so `uvicorn app.main:app` works from the `backend/` directory. (Tests also add it via `tests/conftest.py`.)

## Run

Requires Python 3.10+ and the backend virtual environment:

```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m alembic upgrade head   # create database tables
.venv\Scripts\python ..\scripts\seed_dev.py     # (optional) sample data for local dev
.venv\Scripts\python -m uvicorn app.main:app --reload
```

Then open http://localhost:8000/api/health or http://localhost:8000/docs.

## Database

- Default local development database: SQLite file `amucs_nexus_dev.db` (created next to this README).
- Production target: PostgreSQL. Set `DATABASE_URL` (e.g. `postgresql+psycopg://user:pass@localhost:5432/amucs_nexus`) in `.env`.
- Migrations live in `backend/alembic/` (revisions `0001` and `0002`). On PostgreSQL, real pgvector vector columns require installing the pgvector extension and using a pgvector-aware migration; see `docs/database/`.

## Tests

```bash
cd backend
.venv\Scripts\python -m pytest -q
```

Planned (not built): documents/faculty/research endpoints, authentication, feedback endpoint.
