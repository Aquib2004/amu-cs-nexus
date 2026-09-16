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

## Supported versions

Security updates will be documented here once the project defines release versions.

