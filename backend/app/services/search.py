# services/search.py - search chunks using keyword + semantic + hybrid.
#
# Semantic side:
#   - When a Gemini key is configured, the query is embedded with the same
#     model used at ingestion (gemini-embedding-2, 3072 dims) and matched
#     against the stored chunk embeddings -> real semantic search.
#   - Without a key (or on provider failure) we fall back to the deterministic
#     hash embedder (384 dims), recomputing per-chunk so dimensions always match.

import math
import zlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from ai.retrieval import hybrid as hybrid_alg
from ai.retrieval import keyword as keyword_alg
from ai.retrieval.scoring import cosine_similarity

from app.core.config import settings
from app.models.document import Chunk, Document
from app.schemas.search import SearchResult

# Development/test deterministic embedder matching ingestion HashEmbedder(384).
_DIMS = 384
_SEM_EPSILON = 0.001

_log = __import__("logging").getLogger(__name__)


def _hash_query_vector(text: str) -> list[float]:
    vector = [0.0] * _DIMS
    for token in text.split():
        h = zlib.crc32(token.encode("utf-8")) & 0x7FFFFFFF
        vector[h % _DIMS] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def _real_query_vector(text: str) -> list[float] | None:
    """Embed the query with the production embedder when configured."""
    key = settings.llm_api_key or settings.gemini_api_key
    if not key:
        return None
    try:
        from ai.providers.gemini_embed import GeminiEmbedder

        return GeminiEmbedder(api_key=key).embed(text)
    except Exception as exc:  # provider outage must not break search
        _log.warning("real query embedding unavailable, using hash: %s", exc)
        return None


def _apply_filters(stmt, department: str | None, document_type: str | None):
    if department:
        stmt = stmt.where(Document.department == department)
    if document_type:
        stmt = stmt.where(Document.document_type == document_type)
    return stmt


def search_chunks(
    session: Session,
    query: str,
    limit: int = 10,
    department: str | None = None,
    document_type: str | None = None,
) -> list[SearchResult]:
    # The corpus is small right now (a few hundred chunks), so score every
    # chunk; no candidate truncation, otherwise recent notice docs would crowd
    # out labs/programmes/about content from retrieval entirely.
    stmt = (
        select(Chunk, Document).join(Document, Chunk.document_id == Document.id)
    )
    stmt = _apply_filters(stmt, department, document_type)
    rows = list(session.execute(stmt))

    items = [(str(r.Chunk.id), r.Chunk.text) for r in rows]
    if not items or not query:
        return []

    key_ranking = keyword_alg.rank_keyword(query, items)
    relevant = {rid for rid, score in key_ranking if score > 0.0}

    # --- semantic: real query vector (dims match stored) or hash-per-chunk ---
    query_real = _real_query_vector(query)
    query_hash = _hash_query_vector(query)
    sem_scored: list[tuple[str, float]] = []
    for r in rows:
        chunk = r.Chunk
        stored = chunk.embedding or []
        if query_real is not None and stored and len(stored) == len(query_real):
            score = cosine_similarity(query_real, stored)
        else:
            score = cosine_similarity(query_hash, _hash_query_vector(chunk.text))
        sem_scored.append((str(chunk.id), score))
        if score > _SEM_EPSILON:
            relevant.add(str(chunk.id))
    sem_scored.sort(key=lambda pair: pair[1], reverse=True)

    if not relevant:
        return []

    fused = hybrid_alg.rank_hybrid(key_ranking, sem_scored)
    by_id = {str(r.Chunk.id): (r.Chunk, r.Document) for r in rows}

    results: list[SearchResult] = []
    for chunk_id, score in fused:
        if chunk_id not in relevant or len(results) >= limit:
            continue
        pair = by_id.get(chunk_id)
        if pair:
            chunk, document = pair
            results.append(
                SearchResult(
                    chunk_id=chunk.id,
                    document_id=document.id,
                    text=chunk.text[:300],
                    source_url=document.source_url,
                    score=round(score, 6),
                )
            )
    return results