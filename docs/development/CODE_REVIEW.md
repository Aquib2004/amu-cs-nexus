# AMUCS Nexus — Senior Code Review & Fixed Issues

A release-engineer pass over the codebase. Every item below was **verified** by
running the code (not assumed) and most have been fixed and re-tested.

## Review method
- Read the entire backend, frontend, ai, and ingestion source.
- Installed dependencies, created the env, applied migrations, seeded data.
- Ran all test suites and typed endpoints over live HTTP (curl).
- Attempted a real `npm run build` to surface frontend build issues.

## Verified issues found (and fixed)

### P0 — Would prevent the app from working at all
1. **Backend would not boot outside pytest.**
   `backend/app/services/search.py` imports `ai.retrieval`, but `ai/` lives at
   the repo root. Running `uvicorn app.main:app` crashed with
   `ModuleNotFoundError: No module named 'ai'`; it only worked under pytest
   because `tests/conftest.py` injected the repo root into `sys.path`.
   *Fix:* added `backend/app/bootstrap.py` (adds repo root to `sys.path`) hooked
   from `app/__init__.py`. Verified `import app.main` + live uvicorn boot.

### P1 — Important correctness / integration bugs
2. **No CORS middleware.** A browser UI on `:3000` calling the API on `:8000`
   would be blocked for JSON/POST. *Fix:* added `CORSMiddleware`
   (configurable via `CORS_ORIGINS`). Verified preflight returns
   `access-control-allow-origin: http://localhost:3000`.
3. **Frontend could not build or run `next dev`.**
   - A corrupted Next.js SWC binary (`not a valid Win32 application`) — fixed by
     clean `npm ci`.
   - `package.json` had a UTF-8 **BOM**, breaking Node's JSON parse — removed.
   - `chat/page.tsx` and other script-written files had invalid UTF-8 — recreated.
   - A broken **`C:\Users\<user>\postcss.config.js`** in the home folder was
     auto-loaded by PostCSS (it walks up from the CSS file), crashing builds.
     *Fix:* added a local `frontend/postcss.config.js` (empty plugins) that
     shadows it. Verified `next build` -> "Compiled successfully".
4. **Dev database had no tables when running the app normally.**
   Only pytest created in-memory tables, so `/api/search` failed with
   `no such table: chunks`. *Fix:* documented/verified
   `alembic upgrade head` + `scripts/seed_dev.py`.
5. **Undefined annotations in `notices.py`.** Return types referenced `Notice`
   without importing it (worked only via Python 3.14 deferred annotations).
   *Fix:* changed to `NoticeRead`.
6. **No request validation.** `/api/search` accepted unbounded inputs.
   *Fix:* `Query(min_length, max_length)` + `limit` bounds (1–50), 422 on
   violations. Same for `/api/chat`.

### P2 — Quality / clarity
7. Alembic migration `0002` adds `embedding` as `VARCHAR(8192)` and is not
   pgvector-correct on PostgreSQL. Documented (a real pgvector migration needs
   the extension + provider embeddings) rather than faked.
8. `.env.example` listed `LLM_PROVIDER`/`EMBEDDING_PROVIDER` that nothing uses
   yet — documented as reserved.
9. READMEs claimed endpoints/models were "empty"/"not implemented" when they
   were built — rewritten to match reality.

## Remaining production work
- Production PostgreSQL + pgvector deployment.
- User authentication/accounts and authorization.
- Docker/CI and hosted deployment.
- Richer individual faculty scholarly profiles and additional AMU modules.

Implemented and verified: live AMU ingestion, real embeddings, Gemini/Groq providers, private uploads, exam resources, and anonymous opt-in notifications.

## Note on external integrations
- The AMU **Controller of Examinations** portal may refuse to render inside an
  `<iframe>` because that site sets frame-security headers (X-Frame-Options /
  CSP frame-ancestors). The `/exams` page therefore provides direct links AND an
  optional embedded view, with a clear note — this limitation is in the target
  site, not in our code. Full live result-fetching requires the student's own
  session and is out of scope for a public open-source deploy.

## Final state
- Tests: backend **23**, ai **10**, ingestion **13**; frontend `tsc --noEmit` **0**.
- `next build` succeeds; `npm run dev` serves `/`.
- All fixes committed and pushed to GitHub.