# Tests for the RAG building blocks: evidence, citations, extractive answers.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root -> import ai

from ai.prompts.rag_prompts import UNVERIFIED_ANSWER, build_user_prompt  # noqa: E402
from ai.rag.citations import citations_are_valid, extract_citations  # noqa: E402
from ai.rag.context import build_evidence, format_context  # noqa: E402
from ai.rag.generator import ExtractiveAnswerer, ProviderAnswerer  # noqa: E402


class _FakeResult:
    def __init__(self, number, text, url="https://amu.ac.in/x"):
        from uuid import uuid4

        self.number = number
        self.text = text
        self.source_url = url
        self.document_id = uuid4()
        self.chunk_id = uuid4()


def _evidence():
    results = [
        _FakeResult(0, "The MCA admission notice was published in June 2024."),
        _FakeResult(1, "The computer vision lab has 20 GPU workstations."),
    ]
    return build_evidence(results)


def test_evidence_numbering_and_context() -> None:
    evidence = _evidence()
    assert [e.number for e in evidence] == [1, 2]
    block = format_context(evidence)
    assert "[1]" in block and "amu.ac.in" in block


def test_citation_extraction_and_validation() -> None:
    answer = "Notices exist [1] and more [2]."
    assert extract_citations(answer) == {1, 2}
    assert citations_are_valid(answer, {1, 2})
    # A citation to evidence we never retrieved is invalid (fabrication guard).
    assert not citations_are_valid("Claim [7].", {1, 2})


def test_extractive_answerer_cites_evidence() -> None:
    answer = ExtractiveAnswerer().generate("admission notice date", _evidence())
    assert "[1]" in answer and "admission" in answer.lower()
    assert citations_are_valid(answer, {1, 2})


def test_extractive_answerer_admits_gap() -> None:
    answer = ExtractiveAnswerer().generate("zzzz unknown topic", _evidence())
    assert answer == UNVERIFIED_ANSWER


def test_provider_answerer_requires_wiring() -> None:
    import pytest

    with pytest.raises(NotImplementedError):
        ProviderAnswerer().generate("q", _evidence())
    # The prompt builder used by the provider path is also covered.
    assert "Question:" in build_user_prompt("q", "evidence")