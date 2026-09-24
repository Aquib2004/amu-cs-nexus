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
through ai/rag (evidence -> extractive answer -> cited sources).
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

All responses are JSON; errors are JSON (`{"detail": ...}`). Validation uses
FastAPI/Pydantic (e.g. `/api/search?limit=999` -> 422).

## 4. Backend internals (backend/app/)

- `main.py` — FastAPI app, CORS middleware, router registration.
- `core/config.py` — settings from env / `.env` (pydantic-settings).
- `core/database.py` — SQLAlchemy engine/session, `Base`, `get_db` dependency.
- `core/errors.py` — `AppError` + global 500 handler (safe error responses).
- `core/logging.py` — centralised logging.
- `bootstrap.py` — puts the monorepo root on `sys.path` so `ai` imports work.
- `models/` — ORM: `Document`, `Chunk`, `Notice`, `Faculty`.
- `repositories/` — data-access (documents, notices, faculty).
- `schemas/` — Pydantic request/response contracts.
- `services/` — `search.py` (retrieval) and `chat.py` (RAG).
- `api/` — routers (health, notices, search, chat, documents, faculty, research).
- `alembic/` — migrations `0001..0003` (documents/chunks, embedding col, faculties).

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

- `retrieval/` — `scoring` (cosine, reciprocal-rank fusion), `keyword`,
  `semantic`, `hybrid`. Pure functions, no DB.
- `rag/` — `context` (evidence), `citations` (validation), `generator`
  (`ExtractiveAnswerer` used now; `ProviderAnswerer`=LLM, not wired).
- `prompts/` — system/user prompt templates and the "cannot verify" answer.
- `embeddings/`, `providers/`, `orchestration/`, `evaluation/`, `tools/` —
  placeholders.

## 7. Ingestion (ingestion/)

`url_discovery -> crawler -> html/pdf parser -> cleaner -> metadata -> chunker
-> indexer`. Tested with sample content only; no live AMU crawling. Embeddings
module has a dev `HashEmbedder` and a `ProviderEmbedder` stub.

## 8. Database

- Dev: SQLite `backend/amucs_nexus_dev.db`, created by `alembic upgrade head` +
  `scripts/seed_dev.py`.
- Production target: PostgreSQL (+ pgvector). The `VectorType` column masks the
  difference; a real pgvector migration + provider embeddings are needed for
  production.

## 9. What is used vs. not used (current)

**Used:** FastAPI, Uvicorn, Pydantic(-settings), SQLAlchemy 2, Alembic,
BeautifulSoup, pypdf, httpx, Next.js 14, React 18, TypeScript 5, pytest.

**Not used / deferred (by design):** LangChain, LangGraph, MCP, Redis, Celery,
Kafka, Elasticsearch, dedicated vector database, Kubernetes, microservices,
authentication, real LLM/embedding providers, scheduler, Docker/CI deployment.

## 10. Configuration / environment variables

See `.env.example`: `DATABASE_URL`, `CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`,
`ENVIRONMENT`, `LOG_LEVEL`; reserved (unused yet): `LLM_PROVIDER`,
`LLM_API_KEY`, `EMBEDDING_PROVIDER`, `EMBEDDING_API_KEY`, `REDIS_URL`.

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
## 8. YouRobo (the AI chat assistant)

- **YouRobo** is the name of the chat assistant (branded on the /chat page).
- It uses a Gemini provider when configured, and an offline 'extractive' mode
  otherwise. Both paths return the same response shape with numbered sources.
- Enable Gemini by setting in the backend environment (.env or real env):

      LLM_PROVIDER=gemini
      LLM_API_KEY=...     # or GEMINI_API_KEY=... (alias supported)

- How the provider is wired: i/providers/gemini.py (HTTP client with bounded
  retries and typed errors) <- i/rag/generator.py (GeminiAnswerer) <-
  pp/services/chat.py (chooses provider vs extractive, validates citations).
- No key set? pp/services/chat.py logs INFO and degrades to the extractive
  answerer, so the app keeps working on a fresh clone. Never commit a real key.
- While no key is configured you may see the 
otice field returned from
  /api/chat indicating the extractive path. This is by design (no fabrication).
## Real (live) data ingestion

The database holds real AMU data, not samples, since the real-ingestion work:

- `scripts/ingest_real.py` removes any leftover sample rows, then calls
  `ingestion/app/amu_ingest.py`, which crawls the official AMU department API
  (`https://api.amu.ac.in/api/v1/department-list-data?...`) and upserts:
  notices (paginated, ~160), faculty (18), non-teaching staff (12), programmes
  (5), laboratories, research projects, plus an embedded search/RAG corpus.
- Every crawl writes an `ingestion_log` row (source, rows found/written, status).
- Real embeddings: when `LLM_API_KEY` / `GEMINI_API_KEY` is set, new chunks are
  embedded with `gemini-embedding-2` (3072 dims, free tier) via
  `ai/providers/gemini_embed.py` (key in header only). Without a key, chunks are
  stored un-embedded and search falls back to the deterministic hash embedder.
- Want to re-pull fresh AMU data?

  ```
  cd backend
  .\.venv\Scripts\python.exe -m alembic upgrade head
  .\.venv\Scripts\python.exe ..\scripts\ingest_real.py
  ```

- New directory tables + endpoints: `programs`, `laboratories`,
  `research_projects`, `staff_members` (migration 0004) served at
  `/api/programs`, `/api/laboratories`, `/api/research-projects`, `/api/staff`.
