# AMUCS Nexus - Functional Requirements

Status: DRAFT - Phase 0, for review. Priority: MUST / SHOULD / COULD.

> These describe intended behavior. Implementation happens in later phases; nothing here is built yet.

## 1. Search (MUST)
- F1.1 Provide keyword search over indexed documents and notices.
- F1.2 Provide semantic search over indexed content.
- F1.3 Provide hybrid search combining keyword and semantic signals.
- F1.4 Support metadata filtering (category, date range, department, document type).
- F1.5 Return ranked results with title, snippet, and source link.
- F1.6 Handle empty results gracefully with a clear message.

## 2. Notices (MUST)
- F2.1 List notices, newest first.
- F2.2 Filter notices by date range and category.
- F2.3 Show an individual notice and link to the official source.

## 3. Documents (MUST)
- F3.1 Show a document and its metadata (source URL, type, dates).
- F3.2 Preserve source metadata for every indexed chunk.
- F3.3 Link results to the original PDF or page.

## 4. Faculty (SHOULD)
- F4.1 List faculty with name, designation, areas, and contact.
- F4.2 Search faculty by name and research area.

## 5. Research (SHOULD)
- F5.1 List research areas and publications from indexed sources.
- F5.2 Link to original papers/pages.

## 6. Question answering (MUST)
- F6.1 Accept a question and return an answer plus citations.
- F6.2 Route questions: structured/date/exact vs semantic/hybrid.
- F6.3 Cite sources in the answer (title, type, URL, date, page where available).
- F6.4 Say when information could not be verified instead of inventing details.

## 7. Ingestion (MUST, later)
- F7.1 Discover and crawl official sources respectfully (robots, rate limits).
- F7.2 Parse HTML and PDF to text.
- F7.3 Clean noise and extract metadata.
- F7.4 Chunk text, produce embeddings, index into PostgreSQL + pgvector.
- F7.5 Detect duplicates/changes via content hash; mark outdated sources.

## 8. Feedback (SHOULD)
- F8.1 Accept user feedback on answers/results via /api/feedback.

## 9. Admin / operations (COULD)
- F9.1 Scheduled ingestion runs; visibility into crawl jobs.
- F9.2 Evaluation dashboard over benchmark datasets.

## MVP (first vertical slice)
An end-to-end path that proves the pipeline:

```text
official source -> crawler -> parser -> document -> chunk -> embedding ->
PostgreSQL + pgvector -> retrieval -> FastAPI -> frontend -> answer + citation
```

First focus: official pages, notices, and PDFs. Later: faculty, research, courses.

## Version scope
- **V1:** notices, documents, official pages, search, basic RAG, citations, chat.
- **V2:** faculty, research, courses, metadata filtering, hybrid search, reranking, scheduled ingestion, document versioning.
- **V3:** LangGraph/tools/MCP - only if justified.

