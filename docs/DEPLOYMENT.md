# Deploying AMUCS Nexus

Two services: a FastAPI API and a Next.js frontend. Both deploy free-tier.

## What is in the repository (and what is not)

| Item | In git? | Why |
| --- | --- | --- |
| `data/seed_snapshot.json` (0.2 MB) | Yes | Public AMU content, so a fresh deploy is not empty |
| `backend/amucs_nexus_dev.db` (12 MB) | No | Local build artefact, `*.db` is gitignored |
| Embeddings | No | ~3000 floats per chunk would make the snapshot tens of MB |
| `backend/.env` | No | Secrets are never committed |
| Private uploads / push subscriptions | No | Student data must never be shipped |

Because embeddings are not in the snapshot, a new deployment answers with
keyword + hash scoring until real ingestion runs. Both are correct, just less
semantic. To populate embeddings on the server, run `scripts/ingest_real.py`
there.

## 1. API (Render)

1. Push this repository, then open:
   `https://render.com/deploy?repo=https://github.com/Aquib2004/amu-cs-nexus`
2. Render reads `render.yaml` automatically.
3. In the dashboard, set the secrets (never commit them):
   - `GEMINI_API_KEY` - enables the Gemini chatbot and Gemini embeddings. This
     is the one secret the app needs. Until it is set the chatbot still
     answers, but from the offline extractive fallback, and the API reports
     `"provider": "extractive"` instead of `"gemini"`.
   - `GROQ_API_KEY` - optional alternative (`LLM_PROVIDER=groq`).
4. Note the API URL, e.g. `https://amucs-nexus-api.onrender.com`.
5. Verify: `curl https://<api>/api/health` -> `{"status":"ok",...,"database":"ok"}`

The free plan sleeps after inactivity and its filesystem is ephemeral. That is
fine here: `bootstrap_deploy.py` repopulates from the snapshot on every boot.

`gunicorn` is used on the server (Linux). It cannot run on Windows - use
`uvicorn` locally.

## 2. Frontend (Vercel)

1. Import the repository at vercel.com and set **Root Directory** to `frontend`.
2. Deploy. You get a `https://*.vercel.app` link, and every push to `main`
   redeploys it automatically.

The site is a static export (`next.config.js` sets `output: "export"`), written
to `frontend/out` and committed, because Render's Python runtime has no Node and
cannot run `next build`. Rebuild it whenever frontend source changes:

    cd frontend && npm run build

Two settings here break deployments in ways a health check will not show:

- Do **not** add `outputDirectory` to `vercel.json`. Vercel detects `out/` from
  `next.config.js`; naming it explicitly made every deployment fail while the
  site silently kept serving the previous build.
- Do **not** enable `trailingSlash`. Vercel applies the trailing-slash redirect
  before rewrites run, so `/api/health` answers 308 to `/api/health/` and the
  proxy in section 3 never executes.

## 3. How the frontend reaches the API (nothing to configure)

`frontend/vercel.json` rewrites `/api/*` to the Render origin:

    { "source": "/api/:path*", "destination": "https://amucs-nexus-api.onrender.com/api/:path*" }

Vercel performs that hop on its own edge, so the browser only ever sees the
Vercel host and CORS is never consulted. That is why no `CORS_ORIGINS` entry and
no `NEXT_PUBLIC_API_URL` are required - two values that used to have to be kept
in step by hand every time the frontend origin changed.

`CORS_ORIGINS` on Render still matters for anyone calling the API directly from
another origin; a `*` entry is rejected at startup.

## 4. Share

    - Live app: https://amu-cs-nexus.vercel.app
    - API docs: https://amucs-nexus-api.onrender.com/docs

## 5. Verify

Run the checker after every deploy. It exercises the deployed site the way a
browser does, not just the endpoints:

    python scripts/verify_live.py --api https://amu-cs-nexus.vercel.app

It exits non-zero unless all five hold:

| Check | Failure means | Fix |
| --- | --- | --- |
| API health | API down or database empty | Render logs; confirm `bootstrap_deploy.py` ran |
| Homepage served as HTML | Export not deployed; FastAPI is answering `/` | Rebuild `frontend/out`, push |
| Nested route resolves | Export present but routing broken | Compare `frontend/out` with a fresh build |
| Unknown API route still returns JSON 404 | Frontend middleware is shadowing the API | It must fall through when no file matches |
| Bundle uses the same-origin API base | Bundle hardcodes `http://localhost:8000` | Rebuild `frontend/out`, push |

It deliberately does not follow redirects, so a service parked behind a login
wall is reported as a failure instead of being mistaken for a healthy `200`.

## Security checklist before going public

- [ ] **Set `GEMINI_API_KEY` in the Render dashboard.** The site is public, so
      set it there rather than pasting the key anywhere else. Until then the
      chatbot runs in offline extractive mode.
- [ ] **Rotate `GROQ_API_KEY`.** A key pasted into chat is compromised. Revoke
      in the Groq console and set the new one in the Render dashboard.
- [ ] Confirm `.env`, `*.db`, `*.pem` are not in git: `git ls-files | grep -E "\.env|\.db|\.pem"`
- [ ] Leave `NOTICE_SYNC_ENABLED=false` on the free tier (no scheduler credit).
- [ ] Leave VAPID unset; notifications are simply disabled.

## Local run (Windows)

    # API
    cd backend
    .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

    # Frontend
    cd frontend
    npm run dev