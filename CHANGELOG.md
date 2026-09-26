# Changelog

All notable changes are documented here. Format based on Keep a Changelog; versioning follows Semantic Versioning (yet to be formally released).

## [Unreleased]

### Added
- **Unified YouRobo knowledge answering:** YouRobo now routes questions across
  real faculty, staff, programmes, laboratories, research projects, notices,
  documents, and official examination resources. Exact-name lookup tolerates
  minor student spelling errors (for example, “Armaan Rasool Faridi”).
- **Private file Q&A:** students can upload PDF, DOCX, TXT, or Markdown notes and
  question papers. Only extracted text is retained, access requires a one-time
  token, uploads expire automatically, and questions are isolated to the
  selected file.
- **Live notice updates:** idempotent notices-only synchronization can run from
  the FastAPI lifespan, with opt-in anonymous Web Push subscriptions and automatic
  cleanup of expired/invalid endpoints. Browser permission is requested only
  after the student presses **Enable alerts**.
- **Official exam resources:** `exam_resources` table, `/api/exams`, conservative
  Controller of Examinations ingestion, and exam-aware YouRobo answers. The
  assistant distinguishes official notices from portal guidance and never invents
  schedules, marks, results, or question papers.
- **Migration 0005:** `chat_uploads`, `chat_upload_chunks`,
  `push_subscriptions`, and `exam_resources` tables.
- **Real AMU data (this replaces sample/dev data as the source of truth):**
  - `scripts/ingest_real.py` + `ingestion/app/amu_ingest.py`: crawls the official
    AMU department API (`api.amu.ac.in`) and upserts real records idempotently.
  - Real rows: **18 faculty**, **161 notices**, **12 non-teaching staff**,
    **5 programmes**, laboratories, and research projects.
  - `ingestion/app/exam_ingest.py` stores **23 verified official exam resources**.
  - Migration **0004** adds `programs`, `laboratories`, `research_projects`,
    `staff_members`, `ingestion_log` tables and faculty `image_url`/`source_url`.
  - New endpoints: `GET /api/programs`, `GET /api/laboratories`,
    `GET /api/research-projects`, `GET /api/staff`, `GET /api/exams`.
- **Real embeddings:** `ai/providers/gemini_embed.py` (Gemini `gemini-embedding-2`,
  3072 dims, free tier, key in header only). Ingestion stores vectors in
  `chunks.embedding`; search uses them for genuine semantic ranking with a hash
  fallback when no key is configured.
- **Improved AI answers:** student-focused system prompt, structured intent
  routing, source titles/types in evidence, citation-repair pass, and a safe
  extractive fallback.
- Frontend: YouRobo official/private-file modes, per-answer source panels, file
  picker, notices alert control, and responsive styles.

### Changed
- `chunks.embedding` is now populated with real (3072-dim) Gemini vectors after
  running `ingest_real.py`; the dev hash embedder remains only as a no-key
  fallback in search.
- Backend, frontend, and AI READMEs now reflect implemented status.
- `AMUCS Nexus` brand retained; assistant persona named "YouRobo".

### Fixed
- Backend no longer crashes on start with `ModuleNotFoundError: No module named ai`.
- Notices API return annotations corrected to `NoticeRead`.
- Frontend dev/build blockers (corrupt SWC binary, BOM in files, broken home-directory postcss config).

### Not implemented
- Production PostgreSQL/pgvector deployment, authentication/user accounts, Docker/CI
  deployment, and a hosted push service. Local SQLite, anonymous opt-in Web Push,
  live AMU ingestion, real embeddings, and the complete student-facing directory
  are implemented and tested.
