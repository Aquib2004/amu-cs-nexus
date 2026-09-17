# services/search.py - search chunks using keyword + semantic + hybrid.

import math
import zlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from ai.retrieval import hybrid as hybrid_alg
from ai.retrieval import keyword as keyword_alg
from ai.retrieval import semantic as semantic_alg

from app.models.document import Chunk, Document
from app.schemas.search import SearchResult

# Development/test deterministic embedder matching ingestion HashEmbedder(384).
_DIMS = 384
_SEM_EPSILON = 0.001


def _hash_query_vector(text: str) -> list[float]:
    vector = [0.0] * _DIMS
    for token in text.split():
        h = zlib.crc32(token.encode("utf-8")) & 0x7FFFFFFF
        vector[h % _DIMS] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


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
    candidate_limit = max(limit * 4, 40)
    stmt = (
        select(Chunk, Document)
        .join(Document, Chunk.document_id == Document.id)
        .order_by(Document.crawl_timestamp.desc())
        .limit(candidate_limit)
    )
    stmt = _apply_filters(stmt, department, document_type)
    rows = list(session.execute(stmt))

    items = [(str(r.Chunk.id), r.Chunk.text) for r in rows]
    if not items or not query:
        return []

    key_ranking = keyword_alg.rank_keyword(query, items)
    query_vec = _hash_query_vector(query)
    vec_items = [(str(r.Chunk.id), r.Chunk.embedding or []) for r in rows]
    sem_ranking = semantic_alg.rank_semantic(query_vec, vec_items)

    # Keep only chunks with some real relevance (keyword hit or semantic signal).
    relevant = {
        rid for rid, score in key_ranking if score > 0.0
    } | {
        rid for rid, score in sem_ranking if score > _SEM_EPSILON
    }
    if not relevant:
        return []

    fused = hybrid_alg.rank_hybrid(key_ranking, sem_ranking)
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
