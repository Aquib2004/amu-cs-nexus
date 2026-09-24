# Changelog

All notable changes are documented here. Format based on Keep a Changelog; versioning follows Semantic Versioning (yet to be formally released).

## [Unreleased]

### Added
- **Real AMU data (this replaces sample/dev data as the source of truth):**
  - `scripts/ingest_real.py` + `ingestion/app/amu_ingest.py`: crawls the official
    AMU department API (`api.amu.ac.in`) and upserts real records idempotently.
  - Real rows: **18 faculty** (with photos/emails), **160 notices** (paginated,
    with real dates + PDF links), **12 non-teaching staff**, **5 programmes**
    (B.Sc., MCA, M.Sc., M.Sc. Cyber Security, Ph.D.), **laboratories**, and
    **completed research projects** with funding agencies and investigators.
  - Migration **0004** adds `programs`, `laboratories`, `research_projects`,
    `staff_members`, `ingestion_log` tables and faculty `image_url`/`source_url`.
  - New endpoints: `GET /api/programs`, `GET /api/laboratories`,
    `GET /api/research-projects`, `GET /api/staff`.
- **Real embeddings**: `ai/providers/gemini_embed.py` (Gemini `gemini-embedding-2`,
  3072 dims, free tier, key in header only). Ingestion stores vectors in
  `chunks.embedding`; search uses them for genuine semantic ranking with a
  hash fallback when no key is configured.
- **Improved AI answers**: student-focused `SYSTEM_PROMPT` (concise, cited,
  honest), chat context raised from 5 to 8 evidence chunks, deduplicated
  dimension-aware hybrid search so real content (labs/programmes) is always
  retrievable.
- Frontend: `/programs`, `/laboratories`, `/staff` pages; real photos/emails on
  `/faculty`; real research projects on `/research`; nav + home cards updated.
- `scripts/ingest_real.py` removes fabricated sample rows before ingesting and
  logs every crawl in `ingestion_log`.
- Documentation and project scaffolding: Phases 1-9 (monorepo init, architecture/
  requirements docs, backend foundation, database layer, frontend foundation, API
  integration (notices/search), ingestion pipeline, embeddings field, retrieval search).
- Phase 10 (RAG) + release fixes: `ai/rag` (evidence, citations, extractive
  generator) and `ai/prompts`; `POST /api/chat` RAG endpoint; `/chat` page;
  repository-root `ai` package importable outside pytest; CORS middleware; input
  validation on search/chat.
- Documents / Faculty / Research + Exams: `GET /api/documents`, `GET /api/faculty`,
  `GET /api/research` (migration 0003, directory API tests) + frontend pages.
- YouRobo (Gemini) chatbot: `ai/providers/gemini.py` (bounded retries, typed
  errors, key in header only); `LLM_PROVIDER=gemini` + `LLM_API_KEY` (or
  `GEMINI_API_KEY` alias) with graceful extractive fallback; `/chat` page rebranded.
- UI redesign: AMU logo in header + favicon, modern stylesheet, ADR-002 branding,
  developer guide + `.env.example` docs.

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
- Running PostgreSQL/pgvector, scheduler, authentication, Docker/CI deployment, feedback endpoint, LangChain/LangGraph/MCP.