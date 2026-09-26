# AMUCS Nexus — Developer Guide (How Everything Works)

This guide explains the project end to end: what each component does, where the
code lives, how the pieces connect, and what is (and is not) implemented.

---

## 1. What this project is

AMUCS Nexus is an open-source **information retrieval + AI platform** for the AMU
Department of Computer Science. It is a **modular monolith**: one deployable
application with clearly separated logical subsystems (frontend, backend,
ingestion, AI, database). It is *not* a chatbot-only product — search, documents,
notices, faculty, and research are first-class, so users don't have to "chat" to
find a notice.

Core principle: **source-grounded answers with citations, not hallucination.**

## 2. Repository layout (where everything lives)

```
amu-cs-nexus/
├─ frontend/        Next.js (React + TypeScript) UI  -> runs on :3000
├─ backend/         FastAPI REST API + SQLAlchemy     -> runs on :8000
├─ ingestion/       Crawler/parser/chunker/indexer    (separate entry)
├─ ai/              retrieval + RAG + prompts + embeddings
├─ database/        DB design notes (models live in backend/)
├─ shared/          shared contracts (currently placeholders)
├─ tests/           project-wide test plan (per-suite dirs)
├─ docs/            architecture, api, rag, development, roadmap
├─ infra/           deployment scaffold (Docker/nginx placeholders)
└─ scripts/         seed_dev.py (dev-only seed data)
```

## 3. How a request flows (live, implemented)

```
Browser (:3000) --HTTPS--> Next.js page (client component)
   --fetch--> FastAPI (:8000) /api/...
        -> router (app/api/*.py) -> service (app/services/*.py)
        -> repository (app/repositories/*.py) -> SQLAlchemy -> SQLite (dev)
        -> Pydantic schema (app/schemas/*.py) -> JSON response
Chunks/text go through ai/retrieval (keyword+semantic+hybrid) and for /api/chat
through ai/rag (intent-routed evidence -> provider or extractive answer -> cited sources).
```

### Verified endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | /api/health | service status |
| GET | /api/notices, /api/notices/{id} | notices list / single |
| GET | /api/search?q=&limit=&department=&document_type= | hybrid search |
| POST | /api/chat | grounded answer + cited sources |
| GET | /api/documents, /api/documents/{id} | documents list / detail |
| GET | /api/faculty, /api/faculty/{id} | faculty directory |
| GET | /api/research | research/publication documents |
| GET | /api/programs, /api/laboratories, /api/research-projects, /api/staff, /api/exams | real directory data |
| POST | /api/chat/uploads | private file upload; returns a one-time token |
| DELETE | /api/chat/uploads/{upload_id} | delete private file text |
| GET | /api/notifications/vapid-public-key | opt-in notification configuration |

All responses are JSON; errors are JSON (`{"detail": ...}`). Validation uses
FastAPI/Pydantic (e.g. `/api/search?limit=999` -> 422).

## 4. Backend internals (backend/app/)

- `main.py` — FastAPI app, CORS middleware, router registration.
- `core/config.py` — settings from env / `.env` (pydantic-settings).
- `core/database.py` — SQLAlchemy engine/session, `Base`, `get_db` dependency.
- `core/errors.py` — `AppError` + global 500 handler (safe error responses).
- `core/logging.py` — centralised logging.
- `bootstrap.py` — puts the monorepo root on `sys.path` so `ai` imports work.
- `models/` — ORM: `Document`, `Chunk`, `Notice`, `Faculty`, `Program`, `Laboratory`, `ResearchProject`, `StaffMember`, `ExamResource`, `ChatUpload`, `PushSubscription`.
- `repositories/` — data-access (documents, notices, faculty).
- `schemas/` — Pydantic request/response contracts.
- `services/` — `search.py` (hybrid retrieval), `knowledge.py` (structured intent routing), `chat.py` (RAG), `uploads.py` (private file Q&A), `notice_sync.py` and `push.py`.
- `api/` — routers for health, notices, search, chat/uploads, documents, faculty, research, directory data, exams, and notifications.
- `alembic/` — migrations `0001..0005` (documents/chunks, embeddings, directory tables, uploads/push/exam resources).

## 5. Frontend internals (frontend/src/)

- `app/` — App Router pages: `/`, `/search`, `/notices`, `/chat`, plus
  `/documents`, `/faculty`, `/research`, `/exams`.
- `components/Header.tsx` — top navigation (links for the built areas).
- `services/` — typed API clients (health, notices, search, chat, documents,
  faculty, research).
- `types/` — TS interfaces matching backend JSON.
- `lib/api.ts` — base URL from `NEXT_PUBLIC_API_URL` (default `:8000`).
- `styles/globals.css` — styling.

## 6. AI layer (ai/)

- `rag/` — `context` (evidence), `citations` (validation/repair), `generator` (`ExtractiveAnswerer` and provider-backed answerers), and the extractive fallback.
- `prompts/` — system/user/repair templates and the "cannot verify" answer.
- `providers/` — typed Gemini, Groq, and embedding clients with bounded retries and header-only API keys.
- `retrieval/` — `scoring` (cosine, reciprocal-rank fusion), `keyword`, `semantic`, and `hybrid`. Pure functions, no DB.

## 7. Ingestion (ingestion/)

`amu_ingest.py` crawls the official AMU department API and upserts notices,
faculty, staff, programmes, laboratories, research projects, and an embedded
search corpus. `exam_ingest.py` reads verified Controller of Examinations pages
and upserts the `exam_resources` table. `notice_sync.py` provides a notices-only
background cycle. Embeddings use Gemini `gemini-embedding-2` when a key is
configured, with a deterministic hash fallback for offline development.

## 8. Database

- Dev: SQLite `backend/amucs_nexus_dev.db`, created by `alembic upgrade head` +
  `scripts/seed_dev.py`.
- Production target: PostgreSQL (+ pgvector). The `VectorType` column masks the
  difference; a real pgvector migration + provider embeddings are needed for
  production.

## 9. What is used vs. not used (current)

**Used:** FastAPI, Uvicorn, Pydantic(-settings), SQLAlchemy 2, Alembic,
BeautifulSoup, pypdf, python-docx, pywebpush/py-vapid, httpx, Next.js 14, React 18,
TypeScript 5, pytest.

**Deferred by design:** LangChain, LangGraph, MCP, Redis, Celery, Kafka,
Elasticsearch, dedicated vector database, Kubernetes, microservices,
authentication/user accounts, production PostgreSQL/pgvector, and Docker/CI
deployment.

## 10. Configuration / environment variables

See `.env.example`: `DATABASE_URL`, `CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`,
`ENVIRONMENT`, `LOG_LEVEL`, `LLM_PROVIDER`, `LLM_API_KEY`, `GROQ_API_KEY`,
`GEMINI_API_KEY`, `EMBEDDING_PROVIDER`, `EMBEDDING_API_KEY`, upload expiry,
VAPID keys, and notice-sync settings. `REDIS_URL` remains reserved.

## 11. Running it

```bash
# backend
cd backend
.venv\Scripts\python.exe -m alembic upgrade head
.venv\Scripts\python.exe ..\scripts\seed_dev.py
.venv\Scripts\python.exe -m uvicorn app.main:app --reload

# frontend
cd frontend
npm install
npm run dev
```
Open http://localhost:3000 . API docs: http://localhost:8000/docs .

## 12. Tests

```bash
cd backend;  .venv\Scripts\python.exe -m pytest -q        # 23 pass
cd ai;        backend\.venv\Scripts\python.exe -m pytest tests -q   # 10 pass
cd ingestion; .venv\Scripts\python.exe -m pytest tests -q           # 13 pass
cd frontend; npx tsc --noEmit                          # 0 errors
```
## 13. YouRobo (the AI chat assistant)

- **YouRobo** answers across real faculty, staff, programmes, laboratories,
  research, notices, documents, exam resources, and an optional private file.
- It uses Gemini or Groq when configured and grounded extractive mode otherwise.
  Provider keys are read from the untracked backend `.env`; never commit them.
- Structured intent routing selects the authoritative table for questions about
  people, exams, notices, programmes, laboratories, research, or staff. The LLM
  sees numbered evidence only; citation validation/repair and the extractive
  fallback prevent unsupported claims.
- Private files are token-protected, expiring, and isolated from official search.

### Provider and citation flow

`ai/providers/gemini.py` and `ai/providers/groq.py` implement bounded, typed HTTP
clients. `ai/rag/generator.py` builds a numbered evidence prompt.
`app/services/chat.py` chooses a provider or the extractive answerer, validates
citations, attempts one constrained repair, and falls back if the provider is
unavailable or the answer remains unsafe. The response exposes `provider` and
`notice` so the UI can be honest about how an answer was produced.

## 14. Real (live) data ingestion

`scripts/ingest_real.py` removes leftover sample rows, calls
`ingestion/app/amu_ingest.py` for the official AMU department API, and calls
`ingestion/app/exam_ingest.py` for verified Controller of Examinations pages.
It upserts notices, faculty, staff, programmes, laboratories, research projects,
exam resources, and the embedded search corpus. Every crawl writes an
`ingestion_log` row.

When an embedding key is configured, new chunks are embedded with
`gemini-embedding-2` (3072 dims, free tier) via `ai/providers/gemini_embed.py`;
the key travels only in the request header. Without a key, chunks remain
unembedded and search uses the deterministic hash fallback.

To re-pull data:

```bash
cd backend
.venv\Scripts\python.exe -m alembic upgrade head
.venv\Scripts\python.exe ..\scripts\ingest_real.py
```

Migration 0005 adds `chat_uploads`, `chat_upload_chunks`,
`push_subscriptions`, and `exam_resources`. The notices-only background cycle is
`app/services/notice_sync.py`; browser push delivery is `app/services/push.py`.
