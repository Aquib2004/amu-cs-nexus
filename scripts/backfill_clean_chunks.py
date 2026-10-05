#!/usr/bin/env python
r"""Repair chunk text that still contains HTML entities or invisible characters.

`ingestion/app/cleaner.py` now decodes entities and strips invisible
characters, so newly ingested content is clean. Documents ingested BEFORE that
fix still hold text such as "&nbsp;" and U+FEFF, which breaks tokenisation and
shows up in chat answers.

A full re-ingest would fix this too, but it re-crawls the AMU API and re-embeds
every document, costing time and embedding quota. This script repairs only the
affected chunks, and re-embeds only those, so stored text and vectors stay
consistent.

Usage (from backend/):
    .\.venv\Scripts\python.exe ..\scripts\backfill_clean_chunks.py
    .\.venv\Scripts\python.exe ..\scripts\backfill_clean_chunks.py --dry-run
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
INGESTION = ROOT / "ingestion"
# Inserted at position 0 in reverse so the final order is BACKEND first: the
# backend `app` package must win over ingestion/app, which has the same name.
for _p in (str(INGESTION), str(ROOT), str(BACKEND)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from app.core.config import gemini_embedding_key  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.models.document import Chunk  # noqa: E402


def _load_cleaner():
    """Import ingestion/app/cleaner.py by path.

    It cannot be imported as `app.cleaner` because `app` already resolves to
    the backend package, so the module is loaded from its file instead.
    """
    import importlib.util

    module_path = INGESTION / "app" / "cleaner.py"
    spec = importlib.util.spec_from_file_location("amu_cleaner", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.clean_text


clean_text = _load_cleaner()

logger = logging.getLogger("backfill_clean_chunks")

# Characters that mean "this text was never cleaned".
DIRTY = ("&nbsp;", "&amp;", "&quot;", "&#39;", "&lt;", "&gt;", "&#", "\ufeff", "\u200b", "\u200c", "\u200d", "\u00ad", "\ufffd")


def is_dirty(text: str) -> bool:
    return any(marker in text for marker in DIRTY)


def _embedder():
    key = gemini_embedding_key()
    if not key:
        return None
    from ai.providers.gemini_embed import GeminiEmbedder
    from app.core.config import settings

    return GeminiEmbedder(
        api_key=key,
        timeout=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report only, change nothing")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    session = SessionLocal()
    try:
        chunks = session.query(Chunk).all()
        dirty = [c for c in chunks if is_dirty(c.text or "")]
        logger.info("scanned %d chunks, %d need cleaning", len(chunks), len(dirty))
        if not dirty:
            logger.info("nothing to do; stored chunk text is already clean")
            return 0
        if args.dry_run:
            for c in dirty[:10]:
                logger.info("  would clean: %r", (c.text or "")[:90])
            if len(dirty) > 10:
                logger.info("  ... and %d more", len(dirty) - 10)
            return 0

        embedder = _embedder()
        if embedder is None:
            logger.warning(
                "no embedding key configured: text will be cleaned but the affected "
                "chunks will keep their OLD vectors, which no longer match the text"
            )

        changed = 0
        for chunk in dirty:
            cleaned = clean_text(chunk.text or "")
            if cleaned == chunk.text:
                continue
            chunk.text = cleaned
            if embedder is not None:
                try:
                    vector = embedder.embed(cleaned)
                    if vector and len(vector) == (len(chunk.embedding or []) or len(vector)):
                        chunk.embedding = vector
                except Exception as exc:
                    logger.warning("could not re-embed chunk %s: %s", chunk.id, exc)
            changed += 1
        session.commit()
        logger.info("cleaned and re-embedded %d chunk(s)", changed)
        remaining = [c for c in session.query(Chunk).all() if is_dirty(c.text or "")]
        logger.info("remaining dirty chunks: %d", len(remaining))
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
