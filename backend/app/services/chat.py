# services/chat.py - grounded question answering over indexed content (RAG).
#
# Flow: retrieve relevant chunks -> structure them as numbered evidence ->
# generate an answer strictly from that evidence -> expose the sources for
# citations.
#
# Two generators can answer:
#   * GeminiAnswerer   - real LLM, used when LLM_PROVIDER + LLM_API_KEY are set.
#   * ExtractiveAnswerer - offline fallback that can only re-use evidence text.
#
# Hard rule: the request never fails just because the LLM is unavailable.
# A provider outage degrades to the extractive answer and says so in `notice`.

import logging
from uuid import UUID  # noqa: F401  (kept for type clarity in SourceRef usage)

from sqlalchemy.orm import Session

from ai.providers import GeminiClient, GroqClient, ProviderError
from ai.rag.citations import citations_are_valid
from ai.rag.context import build_evidence
from ai.rag.generator import AnswerGenerator, ExtractiveAnswerer, GeminiAnswerer
from app.core.config import settings
from app.schemas.chat import ChatResponse, SourceRef
from app.services.search import search_chunks

logger = logging.getLogger(__name__)


def _configured_client() -> tuple[GeminiClient | GroqClient, str] | None:
    """Return (client, provider_label) when the LLM provider is fully configured.

    Configuration is a deployment concern, so the decision lives here rather
    than inside the provider package (which must not import app settings).
    Supports both supported free providers via LLM_PROVIDER:
      - "gemini" -> GeminiClient (key: LLM_API_KEY or GEMINI_API_KEY)
      - "groq"   -> GroqClient   (key: GROQ_API_KEY)
    """
    provider = (settings.llm_provider or "").strip().lower()
    if provider == "gemini":
        api_key = settings.llm_api_key or settings.gemini_api_key
        if not api_key:
            logger.info("LLM_PROVIDER=gemini but no key is set; using extractive mode")
            return None
        return (
            GeminiClient(
                api_key=api_key,
                model=settings.llm_model,
                timeout=settings.llm_timeout_seconds,
                max_retries=settings.llm_max_retries,
            ),
            "gemini",
        )
    if provider == "groq":
        api_key = settings.groq_api_key
        if not api_key:
            logger.info("LLM_PROVIDER=groq but no key is set; using extractive mode")
            return None
        return (
            GroqClient(
                api_key=api_key,
                model=settings.groq_model,
                timeout=settings.llm_timeout_seconds,
                max_retries=settings.llm_max_retries,
            ),
            "groq",
        )
    logger.info("LLM_PROVIDER not set to a known provider (%s); extractive mode", settings.llm_provider)
    return None


def answer_question(
    session: Session,
    question: str,
    limit: int = 5,
    department: str | None = None,
    document_type: str | None = None,
    generator: AnswerGenerator | None = None,
) -> ChatResponse:
    """Produce a source-grounded answer and the sources it cites."""
    results = search_chunks(
        session,
        query=question,
        limit=limit,
        department=department,
        document_type=document_type,
    )
    evidence = build_evidence(results)
    evidence_numbers = {item.number for item in evidence}

    # 1. Choose a generator.
    if generator is not None:
        answerer: AnswerGenerator = generator
        provider = "custom"
    else:
        configured = _configured_client()
        if configured is None:
            answerer, provider = ExtractiveAnswerer(), "extractive"
        else:
            client, provider = configured
            answerer = GeminiAnswerer(client)

    notice: str | None = None

    # 2. Generate, degrading instead of failing when the provider misbehaves.
    try:
        answer = answerer.generate(question, evidence)
    except ProviderError as exc:
        logger.warning("LLM provider unavailable, falling back to extractive: %s", exc)
        answer = ExtractiveAnswerer().generate(question, evidence)
        provider = "extractive"
        notice = f"The AI provider was unavailable ({exc}). This answer is an extract of the indexed sources."

    # 3. Final gate: an answer may never cite evidence we did not retrieve,
    #    even if a model produced it. Cheaper to redo than to mislead.
    if not citations_are_valid(answer, evidence_numbers):
        logger.warning("Discarding answer with citations outside the evidence set")
        answer = ExtractiveAnswerer().generate(question, evidence)
        provider = "extractive"
        notice = "The generated answer cited sources that were not retrieved, so it was replaced with a grounded extract."

    sources = [
        SourceRef(
            number=item.number,
            source_url=item.source_url,
            document_id=UUID(item.document_id),
            chunk_id=UUID(item.chunk_id),
            text=item.text,
        )
        for item in evidence
    ]
    return ChatResponse(answer=answer, sources=sources, provider=provider, notice=notice)
