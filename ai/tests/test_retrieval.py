# Tests for the pure retrieval algorithms.

from ai.retrieval import hybrid, keyword, scoring, semantic


def test_cosine_similarity():
    assert scoring.cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert scoring.cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_reciprocal_rank_fusion():
    fused = scoring.reciprocal_rank_fusion([["a", "b"], ["b", "a"]])
    assert fused[0][0] == "a"


def test_keyword_ranks_relevant_first():
    ranked = keyword.rank_keyword(
        "vision", [("x", "hello world"), ("y", "computer vision papers")]
    )
    assert ranked[0][0] == "y"


def test_semantic_ranks_similar_first():
    ranked = semantic.rank_semantic(
        [1.0, 0.0], [("a", [1.0, 0.0]), ("b", [0.0, 1.0])]
    )
    assert ranked[0][0] == "a"


def test_hybrid_fuses():
    fused = hybrid.rank_hybrid([("a", 1.0), ("b", 0.0)], [("b", 0.9)])
    assert fused[0][0] == "b"
