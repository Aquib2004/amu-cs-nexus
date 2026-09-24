# AMUCS Nexus - Project Status

Current phase: **Real AMU data + real embeddings + graduate-ready RAG assistant**
(supersedes the Phase-10 sample-data era).

## What is implemented and verified

### Real-time database (real AMU data, no more samples)
- `scripts/ingest_real.py` + `ingestion/app/amu_ingest.py` crawl the official AMU
  department API (`https://api.amu.ac.in/api/v1/...`, free, no key) and upsert
  idempotently. Every crawl is recorded in `ingestion_log`.
- Current dev DB contents (verified after a live run):
  - **169 documents / 200 chunks** - real about page, 160 real notices, 5 real
    programme pages, laboratories, research projects.
  - **160 notices** with real titles, dates, categories and official PDF links.
  - **18 real faculty** (names, designations, emails, phones, photos, profile
    URLs; Chairperson Prof. Arman Rasool Faridi included).
  - **12 non-teaching staff**, **5 programmes** (B.Sc. Hons, MCA, M.Sc. CS,
    M.Sc. Cyber Security & Digital Forensics, Ph.D.), **laboratories**,
    **2 completed research projects** (UGC / MHRD funded with real PIs).
- Migration **0004**: `programs`, `laboratories`, `research_projects`,
  `staff_members`, `ingestion_log` + faculty `image_url` / `source_url`.

### Real embeddings
- `ai/providers/gemini_embed.py` - Gemini `gemini-embedding-2` (3072 dims,
  free tier, API key in header only). All 200 chunks carry real vectors.
- Search uses them with a hash-embedder fallback (no key / provider down).

### API surface
- Existing: `/api/health`, `/api/notices`, `/api/notices/{id}`, `/api/search`,
  `/api/chat`, `/api/documents`, `/api/documents/{id}`, `/api/faculty`,
  `/api/research`.
- New: `/api/programs`, `/api/laboratories`, `/api/research-projects`,
  `/api/staff`.
- `/api/chat` asks with **8 chunks** of context and a student-focused prompt;
  it returns `provider` (gemini|extractive) and `notice` so the UI is honest.

### Frontend
- `/programs`, `/laboratories`, `/staff` pages added; `/faculty` shows real
  photos/emails; `/research` shows real funded projects; nav + home updated.

## Verification (current run)
- backend `pytest`: **28 passed** (incl. 5 new directory-table tests)
- ai `pytest`: **12 passed**; ingestion `pytest`: **13 passed**
- frontend `tsc --noEmit`: **0 errors**; all pages return 200 live
- Live checks: `/api/search?q=research lab ...` returns real lab content;
  `/api/chat` returns a cited answer (Gemini, falling back gracefully to
  extractive on free-tier rate limits)

## Rebuild the real database anytime
```
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head   # migration 0004
.\.venv\Scripts\python.exe ..\scripts\ingest_real.py # pull real AMU data + embeddings
```

## Remaining (future)
- Real PostgreSQL/pgvector, scheduler (periodic re-crawl), authentication,
  Docker/CI deployment, feedback endpoint, additional AMU modules (publications,
  non-dept pages), faculty detail enrichment (individual scholarly profiles).