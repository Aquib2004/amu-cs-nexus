# ai/rag/context.py - turn ranked search results into numbered evidence (pure logic).
#
# Numbering is the backbone of citations: every answer sentence points back to
# one of these numbers, and every number maps to a real source URL.

from dataclasses import dataclass


@dataclass
class Evidence:
    """One retrievable piece of grounding, numbered for citation."""

    number: int
    text: str
    source_url: str
    document_id: str
    chunk_id: str


def build_evidence(results) -> list[Evidence]:
    """Convert ranked search results into 1-based numbered evidence items."""
    return [
        Evidence(
            number=index,
            text=result.text,
            source_url=result.source_url,
            document_id=str(result.document_id),
            chunk_id=str(result.chunk_id),
        )
        for index, result in enumerate(results, start=1)
    ]


def format_context(evidence: list[Evidence]) -> str:
    """Render evidence as a numbered block (shown to an LLM; also used in logs)."""
    return "\n\n".join(
        f"[{item.number}] {item.text}\n(source: {item.source_url})"
        for item in evidence
    )