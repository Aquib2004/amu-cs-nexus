# AMUCS Nexus - Ingestion

Acquires and processes official AMU / Department of Computer Science source material for retrieval.

> STATUS: Phase 7. Crawler, HTML/PDF parsing, cleaning, metadata extraction, URL discovery, chunking, and an indexer are implemented and unit-tested with sample/local content. We do NOT crawl live AMU sources during development or tests. Embeddings (Phase 8) and the scheduler are not implemented yet.

## Pipeline (implemented parts)

```text
official source
  -> url_discovery   (extract absolute links from HTML)
  -> crawler         (fetch a URL over HTTP)
  -> html_parser     (HTML -> plain text)
  -> pdf_parser      (PDF -> plain text)
  -> cleaner         (normalise whitespace)
  -> metadata        (build source metadata)
  -> chunker         (split text into chunks)
  -> indexer         (persist Document + chunks to the database)
```

## Module map

- `url_discovery.py` - find absolute http(s) links in an HTML page.
- `crawler.py` - `fetch_html(url, client=...)`, injectable for tests.
- `html_parser.py` - `html_to_text`, `extract_title` (BeautifulSoup).
- `pdf_parser.py` - `pdf_to_text` (pypdf, lazy import).
- `cleaner.py` - `clean_text` (collapse spaces/newlines).
- `metadata.py` - `build_metadata` (source_url, title, types, extracted_at).
- `chunker.py` - `split_chunks(text, size, overlap)`.
- `indexer.py` - `index_document(session, document)` persists via the backend models.
- `embedder.py` - placeholder (embeddings come in Phase 8).
- `scheduler.py` - placeholder (scheduled runs come later).

## Tests

```bash
.venv\Scripts\activate
python -m pytest -q
```

9 unit tests cover parsing, cleaning, metadata, chunking, URL discovery, the crawler (mock HTTP transport), and graceful failure.