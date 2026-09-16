# AMUCS Nexus - Frontend

React + TypeScript frontend for AMUCS Nexus, built with Next.js (App Router).

> STATUS: Foundation (Phase 5). Layout, typed API client, health service, and a home page that talks to the backend are implemented. Product areas (Chat, Search, Notices, Documents, Faculty, Research) are stubbed, not built.

## Structure

- `src/app` - App Router pages and layout.
- `src/components` - reusable components (`Header`).
- `src/features` - feature-scoped code (planned: Chat, Search, Notices, ...).
- `src/hooks` - custom hooks (empty).
- `src/lib` - shared helpers (`api.ts` = API base config).
- `src/services` - backend-facing services (`health.ts`).
- `src/types` - TypeScript types (`HealthResponse`, env types).
- `src/utils` - pure helpers (empty).
- `src/styles` - global styles.
- `public` - static assets (empty).
- `tests` - frontend tests (planned).

## Client/server pattern

`src/services/health.ts` shows the client/server flow: the browser (client) sends
an HTTP GET to the FastAPI server and reads the JSON response. The API base URL
comes from `NEXT_PUBLIC_API_URL` (see root `.env.example`) and defaults to
`http://localhost:8000`.

## Run (dependencies installed)

```bash
npm install
npm run dev
```

Open http://localhost:3000. Run the backend first (`uvicorn app.main:app` in
`backend/`) so the home page can show live backend status.

## Verify

```bash
npm run build      # production build + type check
npx tsc --noEmit   # type check only
```

Note: a full `next build` needs a clean, complete `npm install` (the Next.js native
compiler/SWC must be present). If you have a partial/broken install, delete
`node_modules` and run `npm install` again, then `npm run build`.