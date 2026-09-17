# scoring.py - similarity and result fusion helpers (pure, no DB).

import math


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity in [0, 1] between two equal-length vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """Fuse ranked id lists (best first) into one ordered list with scores."""
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, rid in enumerate(ranking, start=1):
            scores[rid] = scores.get(rid, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)
