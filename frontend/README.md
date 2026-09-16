# AMUCS Nexus - Frontend

React + TypeScript frontend for AMUCS Nexus, built with Next.js.

> STATUS: Foundation only. No production UI or features are implemented yet.

## Directory layout

- `src/app` - Next.js App Router pages and route handlers.
- `src/components` - reusable UI components.
- `src/features` - feature-scoped code (Chat, Search, Notices, Documents, Faculty, Research).
- `src/hooks` - custom React hooks.
- `src/lib` - shared internal helpers.
- `src/services` - clients for backend APIs.
- `src/types` - TypeScript types shared across the frontend.
- `src/utils` - pure helper functions.
- `src/styles` - stylesheets.
- `public` - static assets.
- `tests` - frontend tests.

## Planned areas

- Chat
- Search
- Notices
- Documents
- Faculty
- Research

The UI will not force every user through chat. A user looking for a notice should be able to search notices directly.

## Setup (not yet complete)

The frontend is a skeleton. Running `npm install` and `npm run dev` will be documented when the backend API and UI foundation are implemented.

