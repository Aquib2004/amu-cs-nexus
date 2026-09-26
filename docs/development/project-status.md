# AMUCS Nexus - Project Status

Current phase: **Real AMU data + real embeddings + graduate-ready RAG assistant**
(supersedes the Phase-10 sample-data era).

## What is implemented and verified

### Real-time database (real AMU data, no more samples)
- `scripts/ingest_real.py` + `ingestion/app/amu_ingest.py` crawl the official AMU
  department API (`https://api.amu.ac.in/api/v1/...`, free, no key) and upsert
  idempotently. Every crawl is recorded in `ingestion_log`.
- Current dev DB contents (verified after a live run):
  - The corpus contains 169 documents / 200 chunks before exam sync; exam sync adds 23 official exam documents.
  - **161 notices**, **23 official exam resources**, **18 real faculty** (names, designations, emails, phones, photos, profile URLs; Chairperson Prof. Arman Rasool Faridi included), **12 non-teaching staff**, **5 programmes**, laboratories, and research projects.
- Migration **0005** adds `chat_uploads`, `chat_upload_chunks`, `push_subscriptions`, and `exam_resources`.

### Real embeddings
- `ai/providers/gemini_embed.py` - Gemini `gemini-embedding-2` (3072 dims,
  free tier, API key in header only). All 200 chunks carry real vectors.
- Search uses them with a hash-embedder fallback (no key / provider down).

### API surface
- Existing: `/api/health`, `/api/notices`, `/api/notices/{id}`, `/api/search`,
  `/api/chat`, `/api/documents`, `/api/documents/{id}`, `/api/faculty`,
  `/api/research`.
- All directory endpoints: `/api/programs`, `/api/laboratories`, `/api/research-projects`, `/api/staff`, `/api/exams`.
- Upload endpoints: `POST /api/chat/uploads` and `DELETE /api/chat/uploads/{upload_id}`.
- Notification endpoints: `/api/notifications/vapid-public-key`, `/api/notifications/subscriptions`.
- `/api/chat` uses intent-aware structured retrieval plus the hybrid corpus, returns `provider` (`gemini`|`groq`|`extractive`), `source_type`, and a `notice` when degraded.

### Frontend
- `/programs`, `/laboratories`, `/staff` pages added; `/faculty` shows real
  photos/emails; `/research` shows real funded projects; YouRobo supports private
  files and per-answer sources; `/notices` has an opt-in alert control.

## Verification (current run)
- backend `pytest`: **34 passed**; ai `pytest`: **21 passed**; ingestion `pytest`: **13 passed**
- frontend `tsc --noEmit`: **0 errors**; production build verified separately
- Live checks: `/api/search?q=research lab ...` returns real lab content;
  `/api/chat` returns Groq/Gemini answers when configured and falls back safely
  to a grounded extract when a free-tier provider is unavailable.

## Rebuild the real database anytime
```
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head   # migration 0005
.\.venv\Scripts\python.exe ..\scripts\ingest_real.py # real AMU + exam data + embeddings
```

## Remaining (future)
- Production PostgreSQL/pgvector, authentication/user accounts, Docker/CI
  deployment, richer individual faculty scholarly profiles, and a hosted push
  service. Local SQLite, live AMU ingestion, real embeddings, private uploads,
  and anonymous opt-in notifications are implemented and tested.