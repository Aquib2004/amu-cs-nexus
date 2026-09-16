# AMUCS Nexus - Non-Functional Requirements

Status: DRAFT - Phase 0, for review. Targets; verified in later phases.

## Performance
- N1.1 Search/list responses should be fast (target < 300 ms API latency in dev, excluding LLM).
- N1.2 Chat includes LLM latency; keep retrieval overhead low and stream where appropriate.
- N1.3 Avoid premature optimization: measure, then optimize only what matters.

## Security
- N2.1 HTTPS in production; CORS restricted to known origins.
- N2.2 Validate all inputs (URLs, files, request bodies); no SQL injection.
- N2.3 Rate limiting on public endpoints.
- N2.4 Secrets only in env/config; never committed.
- N2.5 Treat retrieved documents as untrusted; documents must never override system instructions (prompt injection defense).
- N2.6 Safe logging (no secrets/PII) and non-verbose error responses.

## Reliability / failure handling
- N3.1 Handle failure in every subsystem: network, invalid input, empty results, malformed/duplicate/outdated documents, crawl/parser/embedding/database/LLM/rate-limit failures.
- N3.2 One failed document must not break the batch.
- N3.3 Graceful degradation: if LLM is unavailable, search still works.

## Verifiability (core to the product)
- N4.1 Every claim must be traceable to a cited source.
- N4.2 The system must not fabricate URLs, dates, or notices.
- N4.3 When uncertain, respond that the information could not be verified.

## Accessibility & UX
- N5.1 Keyboard navigation, semantic HTML, readable typography, focus states, labels, responsive layout.
- N5.2 Users are never forced through chat to reach content.

## Maintainability & testability
- N6.1 Clean, explicit, modular, typed-where-useful code.
- N6.2 Respect subsystem boundaries (frontend/backend/ingestion/database/ai/shared/infra).
- N6.3 Unit, API, integration, security, and AI/evaluation tests accompany features.
- N6.4 Documentation explains both WHAT and WHY.

## Open-source
- N7.1 A contributor can clone, read README, configure .env, install, run, and test without private knowledge.
- N7.2 No secrets, credentials, or private info published.

## Constraints
- Modular monolith; PostgreSQL + pgvector; FastAPI; React/Next.js.
- Do not add LangChain/LangGraph/MCP/Redis/Kafka/Celery/Kubernetes/microservices/Elasticsearch/dedicated vector DB unless a measured requirement appears.

## Risks
- Hallucination; scope creep to full-AMU coverage; page/PDF format changes; legal/policy concerns about scraping; maintaining crawling responsibly.

## Success criteria
- A user finds a notice and opens the official source.
- A user gets a cited answer and can verify each claim.
- Unknown answers are honestly flagged.
- A new contributor runs the project from docs alone.

