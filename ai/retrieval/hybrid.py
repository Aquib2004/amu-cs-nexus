# hybrid.py - combine keyword and semantic rankings by reciprocal-rank fusion.

from .scoring import reciprocal_rank_fusion


def rank_hybrid(
    key_ranking: list[tuple[str, float]],
    sem_ranking: list[tuple[str, float]],
) -> list[tuple[str, float]]:
    """Fuse keyword and semantic id rankings, returning (id, score) best first."""
    key_ids = [rid for rid, _ in key_ranking]
    sem_ids = [rid for rid, _ in sem_ranking]
    return reciprocal_rank_fusion([key_ids, sem_ids])
