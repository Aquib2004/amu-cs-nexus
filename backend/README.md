# AMUCS Nexus - Backend

Python + FastAPI REST API and application logic for AMUCS Nexus.

> STATUS: Foundation only. The health endpoint is implemented; business
> endpoints (search, chat, notices, documents, faculty) are not built yet.

## Structure

- `app/main.py` - FastAPI application entry point.
- `app/api/` - HTTP routers (health.py implemented; others planned).
- `app/core/` - configuration, logging, security.
- `app/models/` - database/domain models (empty).
- `app/schemas/` - request/response schemas (empty).
- `app/services/` - application/business logic (empty).
- `app/repositories/` - data access layer (empty).
- `app/dependencies/` - shared FastAPI dependencies (empty).
- `tests/` - backend tests (empty).

## Run (once dependencies are installed)

From the `backend/` directory:

```bash
python -m venv .venv
.venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://localhost:8000/api/health.

## Planned endpoints (not implemented)

- `GET /api/health` (implemented)
- `GET /api/notices`, `GET /api/notices/{id}`
- `GET /api/documents/{id}`
- `GET /api/faculty`
- `GET /api/search`
- `POST /api/chat`
- `POST /api/feedback`

