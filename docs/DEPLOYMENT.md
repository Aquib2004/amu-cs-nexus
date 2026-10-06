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
   - `GROQ_API_KEY` - chat
   - `GEMINI_API_KEY` - embeddings
4. Note the API URL, e.g. `https://amucs-nexus-api.onrender.com`.
5. Verify: `curl https://<api>/api/health` -> `{"status":"ok",...,"database":"ok"}`

The free plan sleeps after inactivity and its filesystem is ephemeral. That is
fine here: `bootstrap_deploy.py` repopulates from the snapshot on every boot.

`gunicorn` is used on the server (Linux). It cannot run on Windows - use
`uvicorn` locally.

## 2. Frontend (Vercel)

1. Import the repository at vercel.com and set **Root Directory** to `frontend`.
2. Set the environment variable:
   - `NEXT_PUBLIC_API_URL` = your Render API URL
3. Deploy. You get a `https://*.vercel.app` link.

`NEXT_PUBLIC_*` values are inlined at build time, so redeploy after changing it.

## 3. Point the API at the frontend (required)

The API's CORS allowlist is explicit, and a wildcard is rejected at startup.
Set `CORS_ORIGINS` on Render to your Vercel origin (no trailing slash):

    CORS_ORIGINS=https://amu-cs-nexus-2dt6puysf-acme-c82b.vercel.app

Then redeploy the API. Without this the browser blocks every request even though
every endpoint still returns HTTP 200 to curl — a health check cannot catch it.
Run `python scripts/verify_live.py` to confirm the header is actually present.

## 4. Share

The frontend URL is the link to share. For a stable project page, add to the
repository README:

    - Live app: https://<your-app>.vercel.app
    - API docs:  https://<your-api>.onrender.com/docs

## 5. Verify

The three failure modes below all look like "the site is up" to a server-side
health check and only bite a real browser. Run the checker after every deploy:

    python scripts/verify_live.py

It exits non-zero unless all four hold, and names the fix for whichever fails:

| Check | Failure means | Fix |
| --- | --- | --- |
| API health | API down or database empty | Render logs; confirm `bootstrap_deploy.py` ran |
| CORS preflight | API never allowlists the frontend origin | Set `CORS_ORIGINS` on Render, redeploy |
| Frontend public | Redirected to a login wall | Vercel → Settings → Deployment Protection → None |
| Bundle targets API | `NEXT_PUBLIC_API_URL` missing at build time | Set it in Vercel, **redeploy** (build-time var) |

Point it at different hosts with `--api` / `--frontend`. It deliberately does
not follow redirects, because Deployment Protection answers `302` to Vercel SSO
and a client that follows it would report the login page as a healthy `200`.

## Security checklist before going public

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