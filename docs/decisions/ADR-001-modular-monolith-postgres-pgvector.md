# ADR-001 - Modular monolith with PostgreSQL + pgvector

Status: Accepted (Phase 1 architecture).

## Context

AMUCS Nexus is an information retrieval and RAG platform. We need to store structured data (notices, faculty, metadata, feedback) and vector embeddings (for semantic retrieval), and we need the AI to be one component of a larger system.

A common mistake is to over-engineer at the start: microservices, a dedicated vector database, message queues, or an agent framework - before any measured need exists.

## Decision

- Build a **modular monolith**: one deployable system with clearly separated logical subsystems (frontend, backend, ingestion, ai, database, shared, infra).
- Persist structured data in **PostgreSQL**.
- Store embeddings in **pgvector** (a PostgreSQL extension) within the same database.
- Use **file/object storage** for raw PDFs and files when required.
- Do NOT introduce LangChain, LangGraph, MCP, Redis, Kafka, Celery, Kubernetes, Elasticsearch, or a separate vector database unless later measurements create a real requirement.

## Why

### Modular monolith over microservices
Microservices add network, deployment, and operational complexity. For a team of this size, a modular monolith keeps things simple, testable, and deployable while still separating concerns in code.

### pgvector over a separate vector database
PostgreSQL already stores the structured data. pgvector adds vector columns and ANN indexing in the same database, giving:

- one system to operate, back up, and deploy;
- atomic consistency between a document and its embeddings;
- less moving infrastructure and latency.

A dedicated vector database (Pinecone, Qdrant, Weaviate) or Elasticsearch can be re-evaluated if and when load or features justify it.

## Consequences

- **Positive:** simpler ops, fewer dependencies, one source of truth for data, easier for learners to understand.
- **Trade-off:** if the platform grows to very large scale or needs advanced vector features, we may later extract a dedicated vector store. That change is contained to the retrieval/indexing layers.

