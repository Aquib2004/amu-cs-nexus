# ai/rag/generator.py - answer generation strategies.
#
# Two implementations of one interface:
# - ExtractiveAnswerer: offline, composes the answer ONLY from evidence
#   sentences (no model, nothing can be fabricated). Used now for dev/tests.
# - ProviderAnswerer: real LLM, needs provider credentials (later phase).

import re
from abc import ABC, abstractmethod

from ai.prompts.rag_prompts import UNVERIFIED_ANSWER, build_user_prompt
from ai.rag.context import Evidence, format_context

_TOKEN_RE = re.compile(r"[a-z0-9]+")
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


class ProviderAnswerer(AnswerGenerator):
    """LLM-backed generator using SYSTEM_PROMPT + evidence. Needs credentials."""

    def generate(self, question: str, evidence: list[Evidence]) -> str:
        # Assemble the prompt to show the intended shape, then refuse until a
        # provider client exists. Prevents silently shipping an ungrounded path.
        _ = build_user_prompt(question, format_context(evidence))
        raise NotImplementedError("Provider LLM requires provider wiring + credentials")