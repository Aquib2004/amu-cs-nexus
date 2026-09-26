# AMUCS Nexus - Backend

Python + FastAPI REST API and application logic for AMUCS Nexus.

> STATUS: Implemented - health, notices, search, grounded chat (RAG), directory data, exam resources, private uploads, and opt-in notifications. SQLAlchemy models, Alembic migrations, logging, and error handling are wired. No user authentication is configured yet (by design).

## Endpoints

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET  | /api/health        | Service status + identity | - |
| GET  | /api/notices       | List notices (limit/offset) | - |
| GET  | /api/notices/{id}  | Single notice or 404 | - |
| GET  | /api/search        | Hybrid search with filters (q, limit, department, document_type) | - |
| POST | /api/chat          | Source-grounded answer + cited sources (RAG) | - |
| GET  | /api/faculty       | Faculty directory | - |
| GET  | /api/programs, /api/laboratories, /api/research-projects, /api/staff | Real department directory data | - |
| GET  | /api/exams         | Verified official Controller of Examinations resources | - |
| POST | /api/chat/uploads  | Private PDF/DOCX/TXT/Markdown upload; returns a one-time token | Token |
| DELETE | /api/chat/uploads/{upload_id} | Delete private extracted text | Token |
| GET | /api/notifications/vapid-public-key | Opt-in notification configuration | - |

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

Implemented: health, notices, search, grounded chat, directory data, exam resources, private uploads, and anonymous opt-in notifications. Deferred by design: user authentication, production PostgreSQL/pgvector deployment, and Docker/CI deployment.
