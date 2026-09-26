# Tests for the RAG building blocks: evidence, citations, extractive answers.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root -> import ai

from ai.prompts.rag_prompts import UNVERIFIED_ANSWER, build_repair_prompt, build_user_prompt  # noqa: E402
from ai.rag.citations import citations_are_valid, extract_citations  # noqa: E402
from ai.rag.context import build_evidence, format_context  # noqa: E402
from ai.rag.generator import ExtractiveAnswerer, GeminiAnswerer  # noqa: E402
from ai.providers.gemini import GeminiClient  # noqa: E402


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


def test_repair_prompt_lists_only_allowed_citations() -> None:
    prompt = build_repair_prompt(
        "result", "[1] Result portal", "Draft with [9] and [1].", {1, 2}
    )
    assert "ALLOWED CITATION NUMBERS: [1], [2]" in prompt
    assert "[9]" in prompt


def test_extractive_answerer_admits_gap() -> None:
    answer = ExtractiveAnswerer().generate("zzzz unknown topic", _evidence())
    assert answer == UNVERIFIED_ANSWER


class _FakeGeminiClient:
    """Stand-in for GeminiClient so no network/credentials are needed.

    `GeminiAnswerer` takes its client by injection precisely so this is possible.
    """

    def __init__(self, reply: str = "Answer [1]") -> None:
        self.reply = reply
        self.calls: list[tuple[str, str]] = []

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append((system_prompt, user_prompt))
        return self.reply


def test_gemini_answerer_sends_system_prompt_and_evidence() -> None:
    client = _FakeGeminiClient()
    answer = GeminiAnswerer(client).generate("admission notice date", _evidence())

    assert answer == "Answer [1]"
    system_prompt, user_prompt = client.calls[0]
    # The persona/guardrails prompt must reach the model, not be dropped.
    assert "AMU" in system_prompt or "source" in system_prompt.lower()
    # The user turn must carry the question and the numbered evidence block.
    assert "admission notice date" in user_prompt
    assert "[1]" in user_prompt


def test_gemini_answerer_exposes_gemini_contract() -> None:
    """The client is injectable AND the real contract is importable for wiring."""
    assert hasattr(GeminiClient, "generate")


def test_gemini_client_requires_api_key() -> None:
    import pytest

    from ai.providers.gemini import ProviderError

    with pytest.raises(ProviderError):
        GeminiClient(api_key="").generate("system", "user")