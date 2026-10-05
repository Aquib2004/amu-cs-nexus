"""Regression tests for the search relevance gate.

Two distinct scoring modes exist and each needs its own rule:

* real provider embeddings -- a usable relevance signal on its own
* deterministic hash vectors -- CRC32 bucket collisions make them useless as a
  relevance signal, so they may only re-rank keyword hits

The second point was a real bug: the absolute floor (calibrated for real
embeddings) admitted pure noise when no vectors were stored. On the deployed
JSON snapshot, which has no embeddings, "zzzznothing" collided with an
unrelated chunk at 0.577 and returned a result, while the genuine query
"vision" scored only 0.289 and was rejected.
"""

import logging

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.database import Base
from app.models.document import Chunk, Document
from app.services import search as search_module
from app.services.search import search_chunks

logging.disable(logging.CRITICAL)

_engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(_engine)
_session = Session(_engine, expire_on_commit=False)
_doc = Document(
    title="Vision Research",
    source_url="https://amu.ac.in/vision",
    department="computer-science",
    document_type="publication",
)
_doc.chunks.append(Chunk(chunk_index=0, text="papers about computer vision and image processing"))
_session.add(_doc)
_session.commit()


def _force_hash_mode() -> None:
    """Pretend no provider is configured so scoring uses the hash embedder."""
    search_module.gemini_embedding_key = lambda: None  # type: ignore[assignment]


@pytest.fixture(autouse=True)
def _restore_key_resolver():
    original = search_module.gemini_embedding_key
    yield
    search_module.gemini_embedding_key = original  # type: ignore[assignment]


def test_nonsense_query_returns_nothing_without_embeddings() -> None:
    _force_hash_mode()
    assert search_chunks(_session, query="zzzznothing") == []


def test_keyword_match_still_works_without_embeddings() -> None:
    _force_hash_mode()
    results = search_chunks(_session, query="vision", limit=5)
    assert len(results) >= 1
    assert "vision" in results[0].text.lower()


def test_keyword_match_survives_every_spacing_variant() -> None:
    _force_hash_mode()
    for query in ("vision", "Vision", "VISION", "computer vision"):
        assert search_chunks(_session, query=query, limit=5), query


def test_hash_collisions_do_not_create_relevance() -> None:
    """A single-token nonsense query must not surface an unrelated chunk."""
    _force_hash_mode()
    for noise in ("zzzznothing", "xyzzyplugh", "qqqqqqqq", "zzzzzzzz"):
        assert search_chunks(_session, query=noise) == [], noise


def test_empty_and_whitespace_queries_return_nothing() -> None:
    _force_hash_mode()
    assert search_chunks(_session, query="") == []
    assert search_chunks(_session, query="   ") == []