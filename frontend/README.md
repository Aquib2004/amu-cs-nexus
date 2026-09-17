# AMUCS Nexus - Frontend

React + TypeScript frontend for AMUCS Nexus, built with Next.js (App Router).

> STATUS: Home, Search, Notices, and Chat pages are implemented and talk to the backend. Documents, Faculty, and Research remain placeholders (shown as disabled in the header).

## Pages

- `/` - Home: shows live backend health.
- `/search` - Hybrid search over indexed content.
- `/notices` - Recent notices.
- `/chat` - Source-grounded Q&A (RAG) with citations.

## Structure

- `src/app` - App Router pages and layout.
- `src/components` - reusable components (`Header`).
- `src/lib` - shared helpers (`api.ts` = API base config).
- `src/services` - backend-facing services (`health.ts`, `notices.ts`, `search.ts`, `chat.ts`).
- `src/types` - TypeScript types.
- `src/styles` - global styles.

## Client/server pattern

Services send browser HTTP requests to the FastAPI backend. The API base URL comes from `NEXT_PUBLIC_API_URL` (see root `.env.example`) and defaults to `http://localhost:8000`. The backend must run first.

## Run (dependencies installed)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. Run the backend first (see `backend/README.md`).

## Verify

```bash
npx tsc --noEmit   # type check only
npm run build      # production build (a full, clean npm install is required)
```

Note: `next build` uses the Next.js native compiler (SWC). If you have a partial/broken install, delete `node_modules` and re-run `npm install`, then `npm run build`.
