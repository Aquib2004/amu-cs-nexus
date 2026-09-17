# semantic.py - in-memory cosine ranking over stored embeddings.

from .scoring import cosine_similarity


def rank_semantic(
    query_vec: list[float],
    items: list[tuple[str, list[float]]],
    k: int = 10,
) -> list[tuple[str, float]]:
    """Rank (id, vector) pairs by cosine similarity to the query vector."""
    scored = [
        (rid, cosine_similarity(query_vec, vec))
        for rid, vec in items
        if vec
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:k]
