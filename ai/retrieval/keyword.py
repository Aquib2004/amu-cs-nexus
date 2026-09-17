# keyword.py - simple term-overlap keyword ranking.

import re

WORDS = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return WORDS.findall(text.lower())


def score_text(query_tokens: list[str], text_tokens: list[str]) -> float:
    if not query_tokens:
        return 0.0
    found = set(text_tokens)
    return sum(1 for t in query_tokens if t in found) / len(query_tokens)


def rank_keyword(query: str, items: list[tuple[str, str]]) -> list[tuple[str, float]]:
    """Rank (id, text) pairs by term overlap with the query."""
    qt = tokenize(query)
    scored = [(rid, score_text(qt, tokenize(text))) for rid, text in items]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored
