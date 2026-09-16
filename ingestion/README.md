# AMUCS Nexus - Ingestion

Acquires and processes official AMU / Department of Computer Science source material for retrieval.

> STATUS: Stubs only. No crawling, downloading, parsing, or indexing is implemented, and nothing runs during repository initialization.

The eventual pipeline is:

```text
official source -> URL discovery -> crawl -> download -> parse -> clean ->
metadata extraction -> chunk -> embed -> index (PostgreSQL + pgvector)
```

## Modules (intent)

- `url_discovery.py` - find official source URLs.
- `crawler.py` - fetch pages and files.
- `html_parser.py` - parse HTML to clean text.
- `pdf_parser.py` - parse PDFs to text.
- `cleaner.py` - remove noise from parsed text.
- `metadata.py` - capture source metadata.
- `chunker.py` - split text into chunks.
- `embedder.py` - embed chunks for pgvector.
- `indexer.py` - write documents/chunks/embeddings to PostgreSQL.
- `scheduler.py` - schedule repeat ingestion jobs.

This subsystem does NOT blindly scrape every website. It targets official and approved sources only.
