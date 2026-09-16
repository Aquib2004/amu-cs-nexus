# Contributing to AMUCS Nexus

Thank you for your interest in contributing to AMUCS Nexus.

AMUCS Nexus is an open-source knowledge, search, document retrieval, and AI information platform for the Department of Computer Science, Aligarh Muslim University. It is source-grounded and verifiable by design.

## How to contribute

1. Read the code of conduct in `CODE_OF_CONDUCT.md`.
2. Review the documentation under `docs/`, especially `docs/architecture/system-overview.md` and `docs/development/project-status.md`.
3. Look for open issues or propose a new one describing a problem before starting large work.
4. Fork the repository (for public contributions) and create a branch for your change.
5. Implement one logical change per branch.
6. Add or update tests where functionality exists.
7. Document what and why in the relevant `docs/` file.
8. Open a pull request describing the change and the reasoning.

## Development process

The project is built incrementally. Do not add large frameworks or dependencies without an actual engineering requirement (see the engineering decision policy in the main README). Prefer small, reviewable, well-documented changes.

## Commit style

Use clear, conventional commit messages, for example:

- `feat: add notice search endpoint`
- `fix: handle malformed PDF gracefully`
- `docs: document query routing`
- `chore: update dependencies`

## Code expectations

- Clean, readable, explicit, modular code.
- Meaningful names and, where useful, type annotations.
- Educational comments that explain WHY, not just WHAT.
- Respect the subsystem boundaries in the root README (frontend, backend, ingestion, database, ai, shared, infra).

## Reporting bugs

Open an issue with: what happened, what was expected, steps to reproduce, and relevant environment details. Do not include secrets or personal credentials.

## Releases and changelog

Update `CHANGELOG.md` when behavior changes.

