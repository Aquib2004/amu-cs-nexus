# AMUCS Nexus — Comprehensive Bug-Fix Prompt for AI Assistant

## Overview
You are tasked with making the AMUCS Nexus repository (Python/FastAPI backend + Next.js frontend) fully bug-free and production-ready. This is a domain-specific information retrieval platform for Aligarh Muslim University's Computer Science department.

**Repository:** Aquib2004/amu-cs-nexus  
**Tech Stack:** Python 3.10+ (backend/AI/ingestion), Node.js 18+ (frontend), FastAPI, SQLAlchemy, Next.js 14, React 18, SQLite (dev) / PostgreSQL (prod)

---

## Phase 1: Environment & Baseline Validation

### 1.1 Backend Environment Setup & Diagnostics
**File:** `backend/`

Execute these in order and document all output/errors:

```bash
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python ../scripts/seed_dev.py
.venv/Scripts/python -m pytest -q
```

**Must Pass:**
- No `ModuleNotFoundError` for `ai` module
- All migrations apply cleanly
- Seed script completes without error
- All pytest tests pass with 0 failures
- Database file created at `backend/amucs_nexus_dev.db`

**If fails:** Inspect error, fix root cause (import paths, missing deps, migration syntax, schema mismatch)

### 1.2 Frontend Environment Setup & Type Validation
**File:** `frontend/`

```bash
cd frontend
npm install
npx tsc --noEmit
npm run build
```

**Must Pass:**
- No npm install errors
- TypeScript compile with 0 errors
- Next.js build succeeds with "Compiled successfully"

**If fails:** Fix TypeScript errors, Next.js config issues, or missing dependencies

### 1.3 Live Backend Boot Test
**File:** `backend/`

```bash
cd backend
.venv/Scripts/python -m uvicorn app.main:app --reload
```

Navigate to http://localhost:8000/api/health in browser or curl.

**Must Pass:**
- Server starts without exception
- `/api/health` returns 200 with JSON:
  ```json
  {"status": "ok", "application": "AMUCS Nexus", "version": "0.1.0", "environment": "development"}
  ```
- No import/module errors in console
- No database connection errors
- CORS headers present (check Network tab if testing from frontend)

**If fails:** Fix import chains, database setup, or config loading

---

## Phase 2: Configuration & Environment Safety

### 2.1 Environment Variable Validation
**Files:** `backend/app/core/config.py`, `.env.example`

**Checks:**
1. Review `Settings` class in `backend/app/core/config.py`
2. Ensure all optional fields (LLM keys, embedding keys, VAPID keys) have safe defaults
3. If a secret is missing, the app must still boot (not crash on `uvicorn` start)
4. Add explicit fallback messages in logs when optional secrets are absent

**Changes needed:**
- For missing `LLM_API_KEY`/`GEMINI_API_KEY`/`GROQ_API_KEY`: log "INFO: LLM provider keys not set; using extractive fallback"
- For missing `EMBEDDING_API_KEY`: log "INFO: Embedding provider key not set; storing raw text chunks"
- For missing `VAPID_PRIVATE_KEY`: log "INFO: Web Push notifications disabled"
- For missing `DATABASE_URL`: confirm it falls back to `sqlite:///./amucs_nexus_dev.db`

**Test:**
- Start backend WITHOUT a `.env` file — app must boot cleanly
- Add `.env` with only `DATABASE_URL=sqlite:///:memory:` — app must boot
- Verify info logs indicate which features are disabled

### 2.2 CORS Configuration Validation
**File:** `backend/app/main.py`

**Checks:**
1. `CORSMiddleware` is correctly added before routers
2. `allow_origins` is loaded from `CORS_ORIGINS` env var
3. Default is `"http://localhost:3000"`
4. If `CORS_ORIGINS` is empty string, do NOT allow all (`*`) — should be restrictive

**Changes needed:**
- Verify middleware order (must be before `.include_router()` calls)
- Add validation: if CORS_ORIGINS is not set, log warning and use default localhost:3000
- Do NOT silently allow `*` — always be explicit

**Test:**
- Frontend on http://localhost:3000 can POST to http://localhost:8000/api/search
- Preflight OPTIONS request returns correct access-control headers
- A request from wrong origin is blocked

---

## Phase 3: Database & Migrations

### 3.1 Migration Idempotency
**Files:** `backend/alembic/`, `backend/app/models/*.py`

**Checks:**
1. Run `alembic upgrade head` twice — must be idempotent (no errors on second run)
2. Drop database and re-run: `alembic upgrade head` again — must recreate all tables
3. Compare generated schema with actual model definitions in `backend/app/models/`

**Changes needed:**
- Fix any migrations that are not idempotent (e.g., `IF NOT EXISTS` constraints)
- Ensure all model fields match migration column definitions
- Add missing migrations if models were added post-migration

### 3.2 Schema Validation
**Files:** `backend/app/models/*.py` (Document, Chunk, Notice, Faculty, etc.)

**Checks:**
1. Every model column has a type and nullable flag
2. Foreign keys are properly defined with `ForeignKey()` and cascade rules
3. Unique constraints are explicitly set where needed (e.g., `Notice.url`, `Faculty.email`)
4. No circular dependencies between models
5. All relationship backrefs are correct

**Changes needed:**
- Add missing constraints
- Fix nullable inconsistencies (if a field is required in Pydantic schema, it must be non-nullable in DB)
- Verify cascade behavior on delete

### 3.3 Database Boot Safety
**File:** `backend/app/core/database.py`

**Checks:**
1. `SessionLocal` is created without autocommit
2. `get_db()` dependency properly yields and closes sessions
3. Connection timeout handling for PostgreSQL
4. SQLite thread-safety settings are correct

**Changes needed:**
- Ensure `check_same_thread=False` only for SQLite, not PostgreSQL
- Add connection pool settings if using PostgreSQL
- Add exception handling for failed DB connections

---

## Phase 4: API Validation & Error Handling

### 4.1 Request Validation on All Endpoints
**Files:** `backend/app/api/*.py`

**Checks for each endpoint:**
1. All `Query` parameters have `min_length` and/or `max_length` bounds
2. All integer parameters have `ge` (>=) and `le` (<=) bounds
3. All required fields are explicit
4. All optional fields have `None` defaults
5. UUIDs are properly typed (`UUID`, not `str`)

**Priority endpoints to fix:**
- `/api/search` — query `q` must be min 1, max 300; `limit` must be 1-50
- `/api/chat` — question min 1, max 500; `limit` 1-20; upload fields optional
- `/api/notices` — limit/offset bounds
- `/api/faculty`, `/api/documents`, `/api/programs` — limit/offset bounds

**Changes needed:**
- Add missing bounds to all Query parameters
- Replace bare `str` with `Field(..., min_length=1, max_length=X)` patterns
- Add 422 tests to pytest suite for invalid inputs

**Test:**
- Send empty query to `/api/search?q=` — must return 422
- Send query > 300 chars to `/api/search` — must return 422
- Send `limit=0` to `/api/search` — must return 422
- Send invalid UUID to `/api/notices/{id}` — must return 422

### 4.2 Error Handler Coverage
**File:** `backend/app/core/errors.py`

**Checks:**
1. `AppError` class catches expected, user-safe errors
2. Generic `Exception` handler logs full traceback but returns generic 500
3. No internal stack traces or sensitive info in response JSON

**Changes needed:**
- Verify `register_error_handlers(app)` is called in `main.py`
- Add handler for `ValueError`, `TypeError` if they escape business logic
- Ensure all 404 returns use `HTTPException(status_code=404, detail="...")`

**Test:**
- Trigger a 404 — response must have only `{"detail": "..."}`
- Trigger a validation error — response must have `{"detail": "..."}` with no traceback
- Backend logs must have full exception info

### 4.3 Endpoint Return Type Validation
**Files:** `backend/app/schemas/*.py`

**Checks:**
1. Every endpoint has a `response_model` specified
2. Response schema fields match actual returned data types
3. No `Any` types in schemas

**Changes needed:**
- Add `response_model` to any endpoint missing it
- Fix type mismatches (e.g., if returning list but schema expects single object)
- Replace `Any` with concrete types

---

## Phase 5: Search & Retrieval Correctness

### 5.1 Search Endpoint Safety
**File:** `backend/app/services/search.py`

**Checks:**
1. Empty query is rejected at API layer (already done via validation)
2. No-match returns `[]` not error
3. Metadata filters (department, document_type) are optional and safe
4. Result ordering is deterministic
5. No duplicate results
6. Source URLs are valid

**Changes needed:**
- Add null check: if `search_chunks()` returns None, return `[]`
- Verify limit is applied correctly
- Test with queries that have no results

**Test:**
- `/api/search?q=zzzznothing` must return `[]`, not 500
- `/api/search?q=vision&department=invalid` must return `[]` (no error)
- `/api/search?q=vision` must return same order on repeat calls

### 5.2 Chat Service Fallback Logic
**File:** `backend/app/services/chat.py`

**Checks:**
1. If LLM provider is not configured, use extractive fallback
2. If LLM provider fails, catch exception and use fallback
3. If no sources found, return honest "cannot verify" message
4. Citation validation does not crash on malformed sources

**Changes needed:**
- Add try-except around LLM calls with fallback to extractive
- Add logging for provider failures
- Test with missing `GEMINI_API_KEY` — should still return valid chat response
- Verify "notice" field is set when degrading to fallback

**Test:**
- POST `/api/chat` with no LLM key configured — must return 200 with extractive answer
- POST `/api/chat` with invalid LLM key — must return 200 with extractive answer
- POST `/api/chat` with query not in index — must return honest "cannot verify" message

### 5.3 Knowledge Routing Safety
**File:** `backend/app/services/knowledge.py`

**Checks:**
1. `_domains()` function handles empty query
2. Domain detection does not crash on special characters
3. Fallback to generic search if no domain matches
4. Scoring functions handle empty/None inputs

**Changes needed:**
- Add guards for None/empty strings
- Test with Unicode, emojis, SQL-like strings
- Verify no regex DoS patterns

---

## Phase 6: AI Provider Fallback & Graceful Degradation

### 6.1 LLM Provider Safety
**Files:** `ai/providers/gemini.py`, `ai/providers/groq.py` (if exists)

**Checks:**
1. Provider initialization does NOT crash if API key is missing
2. Provider calls have timeout limits
3. HTTP errors (5xx, rate limits) are caught and logged
4. Fallback to extractive mode if provider is down
5. No infinite retry loops

**Changes needed:**
- Add `try-except` around provider instantiation
- Verify timeout is set (currently `llm_timeout_seconds: float = 20.0`)
- Add retry logic with `llm_max_retries: int = 2` but NEVER retrying endlessly
- Log provider errors at WARNING level, not silent

**Test:**
- Start backend with `LLM_API_KEY=invalid` — must boot and use extractive
- Simulate provider timeout (mock `httpx.Client.post()` to delay > 20s) — must fall back
- Simulate provider 500 error — must fall back

### 6.2 Embedding Provider Safety
**Files:** `ai/providers/gemini_embed.py` (if exists), `ai/embeddings/`

**Checks:**
1. If embedding provider is not configured, store text chunks without embeddings
2. If embedding call fails, do NOT crash ingestion — log warning
3. Chunk text is always stored even if embedding fails

**Changes needed:**
- Verify `ingestion/app/amu_ingest.py` has `try-except` around embedding calls
- Confirm warning is logged: `logger.warning("embedding failed, storing raw chunks: %s", exc)`
- Test ingestion without embedding key

**Test:**
- Run ingestion with `EMBEDDING_API_KEY` unset — must ingest documents
- Run ingestion with `EMBEDDING_API_KEY=invalid` — must log warning and ingest anyway

---

## Phase 7: Upload Pipeline Robustness

### 7.1 File Parsing Safety
**Files:** `ingestion/pdf_parser.py`, `ingestion/app/*.py` (docx, text parsing)

**Checks:**
1. PDF parsing handles empty PDFs
2. DOCX parsing handles corrupted files
3. Text parsing handles invalid UTF-8
4. No parser crashes on file errors — all exceptions logged
5. Original binary file is NOT persisted

**Changes needed:**
- Add `try-except` around each parser with `except Exception as e: logger.error(...)`
- Test with corrupted/empty files
- Verify only extracted text is stored, not binary

**Test:**
- Upload empty PDF — must parse without crash, return empty text
- Upload corrupted DOCX — must handle gracefully
- Upload text with invalid UTF-8 — must handle or skip bytes

### 7.2 Private Upload Token Safety
**File:** `backend/app/api/chat.py`, `backend/app/services/uploads.py`

**Checks:**
1. Upload token is validated before use
2. Token is never logged or returned insecurely
3. Expiry is enforced (24 hours by default)
4. Invalid/expired tokens return 401 not 500
5. Text extraction from uploads is sanitized

**Changes needed:**
- Add token validation at endpoint entry
- Return 401 if token invalid/expired
- Do NOT log token in debug output
- Verify upload model has `expires_at` timestamp

**Test:**
- POST `/api/chat/uploads` without token — must validate
- POST `/api/chat` with invalid upload_token — must return 401
- POST `/api/chat` with expired upload_token — must return 401

---

## Phase 8: Frontend Runtime & Build Safety

### 8.1 TypeScript Strict Mode
**File:** `frontend/tsconfig.json`

**Checks:**
1. `"strict": true` is set
2. `"noImplicitAny": true`
3. `"strictNullChecks": true`
4. No `// @ts-ignore` comments (except where unavoidable)

**Changes needed:**
- Enable strict mode flags
- Fix all TypeScript errors before build
- Run `npx tsc --noEmit` and ensure 0 errors

### 8.2 API Response Handling
**Files:** `frontend/src/**/*.tsx`, `frontend/src/**/*.ts`

**Checks:**
1. All `fetch()` calls have error handling
2. Response JSON parsing is wrapped in `try-catch`
3. Assume API response fields might be missing (defensive programming)
4. Network errors (timeout, no internet) are handled

**Changes needed:**
- Add `.catch()` to all fetch calls
- Add `response.ok` check before parsing JSON
- Add null-checks on response fields
- Display user-friendly error messages

**Test:**
- Simulate backend offline — frontend must show error, not crash
- Simulate malformed JSON response — frontend must show error

### 8.3 Frontend Build Correctness
**File:** `frontend/next.config.js`, `frontend/postcss.config.js`

**Checks:**
1. `next build` completes without errors
2. No broken imports in pages or components
3. Environment variables are correctly loaded from `NEXT_PUBLIC_*`
4. PostCSS config does not walk up to home directory (already fixed, but verify)

**Changes needed:**
- Run `npm run build` and ensure success
- Verify all build artifacts are generated
- Test that built app runs with `npm start`

---

## Phase 9: Background Tasks & Async Safety

### 9.1 Notice Sync Loop
**File:** `backend/app/main.py`, `backend/app/services/notice_sync.py`

**Checks:**
1. Loop does NOT crash on first-time missing database
2. Loop catches and logs exceptions without stopping
3. Loop respects `notice_sync_enabled` flag (default False)
4. Graceful shutdown cancels loop without hanging
5. No memory leaks from repeated task creation

**Changes needed:**
- Verify `notice_sync_enabled` defaults to `False` (it does)
- Add `try-except` in loop to catch service errors
- Verify `lifespan` context manager cleans up properly

**Test:**
- Start backend with `NOTICE_SYNC_ENABLED=true` — must not crash
- Simulate notice sync failure — must log error and continue
- Stop backend (Ctrl+C) — should gracefully cancel task

---

## Phase 10: Security Hardening

### 10.1 No Secrets in Code
**Check:**
- No API keys, passwords, or tokens in `.py` files
- `.env` is in `.gitignore` (verify `.gitignore`)
- `.env.example` contains only placeholder values

**Changes needed:**
- Audit code for hardcoded secrets
- Verify `.env` is ignored
- Document secret setup in SECURITY.md

### 10.2 SQL Injection Prevention
**Files:** All `backend/app/repositories/`, `backend/app/services/`

**Checks:**
1. No f-string SQL queries
2. All DB queries use parameterized statements (SQLAlchemy ORM)
3. No raw SQL except through SQLAlchemy `text()` with explicit parameter bindings

**Changes needed:**
- Replace any dynamic queries with ORM equivalents
- Use `text()` only with explicit bind params

### 10.3 Path Traversal Prevention
**Files:** `ingestion/pdf_parser.py`, any file handling

**Checks:**
1. No `os.path.join()` with untrusted paths
2. No `open(user_input_path)` directly
3. File operations are sandboxed to upload directory

**Changes needed:**
- Use `pathlib.Path` with explicit parent checks
- Validate file extensions against whitelist

---

## Phase 11: Final Validation & Testing

### 11.1 Complete Test Suite
**Commands:**
```bash
cd backend
.venv/Scripts/python -m pytest -q --tb=short

cd ../ai
python -m pytest tests -q --tb=short

cd ../ingestion
python -m pytest tests -q --tb=short

cd ../frontend
npx tsc --noEmit
npm run build
```

**Must Pass:** All tests pass, 0 errors, 0 warnings

### 11.2 Smoke Test Workflow
**Commands:**
```bash
# Backend
cd backend
.venv/Scripts/python -m uvicorn app.main:app --reload &

# Frontend
cd frontend
npm run dev &

# Wait for both to boot, then test manually
curl http://localhost:8000/api/health
curl http://localhost:8000/api/notices
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Who is the faculty?"}'

# Open http://localhost:3000 in browser and test search/chat UI
```

**Must Pass:**
- All endpoints return valid JSON
- Frontend loads and connects to API
- Chat/search functionality works end-to-end
- No console errors in browser DevTools

### 11.3 Edge Case Testing
**Test each scenario:**
1. Empty/null queries → graceful response
2. Very long queries → rejected with 422
3. Invalid UUIDs → 422
4. Missing auth tokens → 401
5. Expired uploads → 401
6. Database unavailable → 500 with safe message
7. LLM provider down → extractive fallback with notice
8. Invalid JSON requests → 422
9. CORS preflight → 200 with correct headers
10. Shutdown during request → graceful cleanup

---

## Phase 12: Documentation & Production Readiness

### 12.1 Update README & Docs
**Files:** `README.md`, `docs/development/DEVELOPER_GUIDE.md`

**Add:**
- Prerequisites (Python 3.10+, Node.js 18+, etc.)
- Exact setup commands for fresh clone
- All env vars with descriptions
- Known limitations
- Troubleshooting section

### 12.2 Add Health Check Endpoint Enhancements
**File:** `backend/app/api/health.py`

**Add optional checks:**
- Database connectivity
- AI provider availability (optional)
- Disk space

---

## Success Criteria

Your fixes are complete when:

✅ Backend starts without errors: `uvicorn app.main:app`  
✅ All backend tests pass: `pytest -q`  
✅ Frontend builds without errors: `npm run build`  
✅ Frontend TypeScript compiles: `tsc --noEmit`  
✅ `/api/health` returns 200 from browser  
✅ `/api/search?q=test` returns valid JSON  
✅ `/api/chat` handles valid and invalid input gracefully  
✅ All optional features degrade gracefully when env vars missing  
✅ Database boots cleanly on fresh clone  
✅ No exceptions logged on startup  
✅ No secrets in code or logs  
✅ All 10 test scenarios pass (Phase 11.3)  
✅ Frontend chat/search UI works end-to-end  
✅ Both backend and frontend shutdown cleanly (Ctrl+C)

---

## Implementation Order

1. **Phase 1:** Get baseline passing (tests, builds, boot)
2. **Phase 2:** Config safety
3. **Phase 3:** Database correctness
4. **Phase 4:** API validation
5. **Phase 5:** Search/chat logic
6. **Phase 6:** Provider fallbacks
7. **Phase 7:** Upload safety
8. **Phase 8:** Frontend safety
9. **Phase 9:** Background tasks
10. **Phase 10:** Security
11. **Phase 11:** Comprehensive testing
12. **Phase 12:** Documentation

---

## How to Report Bugs

As you fix, create one GitHub issue per bug category:
- **Category:** Config, Database, API, Search, AI, Upload, Frontend, Async, Security
- **Severity:** P0 (won't boot), P1 (breaks feature), P2 (degrades gracefully)
- **Description:** What was broken, what the fix was, how to verify
- **Test case:** Exact command/request that proves it's fixed
