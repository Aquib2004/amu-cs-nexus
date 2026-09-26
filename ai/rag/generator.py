# ai/rag/generator.py - answer generation strategies.
#
# Two implementations of one interface:
# - ExtractiveAnswerer: offline, composes the answer ONLY from evidence
#   sentences (no model, nothing can be fabricated).
# - GeminiAnswerer: provider-backed generation, with the citation gate and
#   extractive fallback applied by the backend service.

import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ai.prompts.rag_prompts import SYSTEM_PROMPT, UNVERIFIED_ANSWER, build_user_prompt
from ai.rag.context import Evidence, format_context

# Imported for typing only: this module must not construct clients (credentials
# belong to the app layer), so a real import at runtime is unnecessary here.
if TYPE_CHECKING:  # pragma: no cover - typing-only branch
    from ai.providers.gemini import GeminiClient

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_BROAD_LIST_NOUNS = {
    "laboratories", "labs", "laboratory", "exams", "examinations", "exam",
    "staff", "programmes", "programs", "courses", "projects", "faculty",
}
# Small stopword list so generic words don't drive sentence selection.
_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "of", "for", "to", "in",
    "on", "at", "what", "which", "who", "and", "or", "about", "by", "with",
}


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS}


class AnswerGenerator(ABC):
    """Common interface for producing an answer from evidence."""

    @abstractmethod
    def generate(self, question: str, evidence: list[Evidence]) -> str:
        """Return an answer grounded in (and citing) the evidence."""
        raise NotImplementedError


class ExtractiveAnswerer(AnswerGenerator):
    """Picks the best-matching evidence sentences and cites their sources.

    Because output is a subset of evidence text, unsupported claims are
    impossible by construction -- the safest possible baseline before an LLM.
    """

    max_sentences: int = 3

    def generate(self, question: str, evidence: list[Evidence]) -> str:
        question_tokens = _tokens(question)
        scored: list[tuple[int, int, str]] = []  # (overlap, evidence_number, sentence)
        for item in evidence:
            for sentence in re.split(r"(?<=[.!?])\s+|\n+", item.text):
                sentence = sentence.strip()
                if not sentence:
                    continue
                overlap = len(question_tokens & _tokens(sentence))
                if overlap:
                    scored.append((overlap, item.number, sentence))

        # Best overlap first; on ties prefer earlier evidence (higher-ranked).
        scored.sort(key=lambda entry: (-entry[0], entry[1]))
        if not scored:
            # Broad list questions (for example, "what are the laboratories?")
            # can have authoritative rows whose wording does not repeat the
            # question. Quote the top evidence instead of claiming a gap.
            broad_list = bool(set(_TOKEN_RE.findall(question.lower())) & _BROAD_LIST_NOUNS)
            if evidence and broad_list:
                first = evidence[0].text.strip().replace("\n", " ")
                return f"{first[:600]} [{evidence[0].number}]"
            return UNVERIFIED_ANSWER

        chosen: list[str] = []
        seen: set[str] = set()
        for _, number, sentence in scored:
            key = sentence.lower()
            if key in seen:
                continue
            seen.add(key)
            chosen.append(f"{sentence} [{number}]")
            if len(chosen) >= self.max_sentences:
                break
        return " ".join(chosen)


class GeminiAnswerer(AnswerGenerator):
    """LLM-backed generator: SYSTEM_PROMPT + numbered evidence -> cited answer.

    The client is injected rather than constructed here. That keeps this class
    free of configuration/credential concerns and lets tests pass a fake client
    that returns canned text (including misbehaving text).
    """

    def __init__(self, client: "GeminiClient") -> None:
        self._client = client

    def generate(self, question: str, evidence: list[Evidence]) -> str:
        user_prompt = build_user_prompt(question, format_context(evidence))
        # Provider failures deliberately propagate: `services/chat.py` catches
        # ProviderError and degrades to the extractive answer, so an outage
        # never turns into a 500 for the user.
        return self._client.generate(SYSTEM_PROMPT, user_prompt)