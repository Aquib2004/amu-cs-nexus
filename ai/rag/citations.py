# ai/rag/citations.py - citation extraction and validation (pure functions).
#
# This is the anti-hallucination gate: an answer may only cite evidence
# numbers that actually exist in the retrieved set.

import re

_CITATION_RE = re.compile(r"\[(\d{1,3})\]")


def extract_citations(answer: str) -> set[int]:
    """Return the set of citation numbers used in an answer, e.g. '[2]' -> {2}."""
    return {int(match) for match in _CITATION_RE.findall(answer)}


def citations_are_valid(answer: str, evidence_numbers: set[int]) -> bool:
    """True only if every cited number exists in the evidence set."""
    return all(number in evidence_numbers for number in extract_citations(answer))