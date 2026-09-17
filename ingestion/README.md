# AMUCS Nexus - Ingestion

Acquires and processes official AMU / Department of Computer Science source material for retrieval.

> STATUS: Implemented and unit-tested with sample/local content. Crawler, HTML/PDF parsing, cleaning, metadata extraction, URL discovery, chunking, a deterministic dev embedder, and an indexer. We do NOT crawl live AMU sources during development or tests. The scheduling layer is not implemented.

## Pipeline

```text
official source
  -> url_discovery   (extract absolute links from HTML)
  -> crawler         (fetch a URL over HTTP; injectable client for tests)
  -> html_parser     (HTML -> plain text)
  -> pdf_parser      (PDF -> plain text, pypdf)
  -> cleaner         (normalise whitespace)
  -> metadata        (build source metadata)
  -> chunker         (split text into chunks)
  -> indexer         (persist Document + chunks to the database)
```

Embeddings (Phase 8): the `embedder.py` module provides a deterministic dev `HashEmbedder` and a `ProviderEmbedder` interface for real providers. The backend `Chunk.embedding` column and a portable vector type exist; production embeddings/pgvector need a provider key and a running PostgreSQL.

## Tests

```bash
.venv\Scripts\activate
python -m pytest -q
```

Unit tests cover parsing, cleaning, metadata, chunking, URL discovery, the crawler (mock HTTP transport), the dev embedder, and graceful failures.
