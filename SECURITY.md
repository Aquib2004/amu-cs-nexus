# Security Policy

## Reporting a vulnerability

If you discover a security vulnerability in AMUCS Nexus, please report it privately to the maintainers rather than opening a public issue.

When reporting, include:

- A description of the vulnerability and its impact.
- Steps to reproduce it.
- Affected versions, if known.

## Security principles for AMUCS Nexus

- Never commit API keys, passwords, or private credentials. Keep secrets in local `.env` files that are excluded from Git.
- Treat retrieved documents and user input as untrusted data.
- Retrieved documents must never override application/system instructions (prompt injection defense).
- Validate all inputs: URLs, files, and request bodies.
- Log safely: do not log secrets or sensitive personal data.
- Return secure, non-verbose error responses.

## Secret setup

All secrets live in an untracked `backend/.env` (or environment variables in
production). Copy `backend/.env.example` and fill in only what you need. Every
optional secret degrades gracefully when absent:

| Variable | If missing |
| --- | --- |
| `LLM_API_KEY` / `GEMINI_API_KEY` / `GROQ_API_KEY` | App boots; chat uses the extractive, no-fabrication fallback. Logs an INFO line. |
| `EMBEDDING_API_KEY` / `GEMINI_API_KEY` | Search and ingestion use the deterministic local hash embedder; raw text chunks are still stored. |
| `VAPID_PRIVATE_KEY` / `VAPID_PRIVATE_KEY_FILE` | Web Push is disabled; the VAPID endpoint reports `enabled: false`. |
| `DATABASE_URL` | Falls back to `sqlite:///./amucs_nexus_dev.db`. |
| `CORS_ORIGINS` | Defaults to `http://localhost:3000` in development. In production an empty value allows no browser origins. A `*` entry is rejected at startup. |

The VAPID private key and provider keys are never returned by any endpoint, and
private-upload access tokens are stored only as SHA-256 hashes.

## Behaviour that is security-relevant

- **Private uploads** are never added to the public search index. The original
  binary is discarded after text extraction, and access requires a matching
  bearer token. An invalid or expired token returns `401`, never `500`, and the
  token is never logged. Uploads expire automatically (24h by default) and are
  purged on startup and on a recurring interval.
- **Error responses** never contain stack traces, driver errors, or internal
  details. `AppError` returns its client-safe message; unexpected exceptions are
  logged server-side and returned as a generic `500`.
- **Request validation** is enforced at the API layer (`422` for empty or
  oversized queries, out-of-range pagination, and malformed UUIDs), so invalid
  input is rejected before it reaches business logic.
- **CORS** never allows a wildcard. Unknown origins receive no
  `access-control-allow-origin` header.
- **Database queries** use the SQLAlchemy ORM or `text()` with explicit bind
  parameters; no user input is interpolated into SQL.
- **Sample seeding** is refused against any database that already holds real AMU
  records, so fake faculty or notices can never be mixed into real content.

## Rotating a leaked key

If a key is ever pasted into a chat, issue, or commit:

1. Revoke it in the provider console and generate a replacement.
2. Update the untracked `backend/.env`.
3. Confirm with a repository-wide secret scan that the old value is gone.
## Supported versions

Security updates will be documented here once the project defines release versions.


