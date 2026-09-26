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
from uuid import UUID

from sqlalchemy.orm import Session

from ai.providers import GeminiClient, GroqClient, ProviderError
from ai.prompts.rag_prompts import UNVERIFIED_ANSWER, build_repair_prompt
from ai.rag.citations import citations_are_valid, extract_citations
from ai.rag.context import build_evidence, format_context
from ai.rag.generator import AnswerGenerator, ExtractiveAnswerer, GeminiAnswerer
from app.core.config import settings
from app.schemas.chat import ChatResponse, SourceRef
from app.services.knowledge import search_knowledge
from app.services.uploads import get_authorized_upload, search_upload

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
    upload_id: UUID | None = None,
    upload_token: str | None = None,
) -> ChatResponse:
    """Produce a cited answer from official data or one private upload."""
    if upload_id is not None:
        upload = get_authorized_upload(session, upload_id, upload_token)
        results = search_upload(upload, question, limit=limit)
    else:
        results = search_knowledge(session, question, limit=limit)
    evidence = build_evidence(results)
    evidence_numbers = {item.number for item in evidence}

    # No evidence means no model call and no opportunity to invent an answer.
    if not evidence:
        return ChatResponse(
            answer=UNVERIFIED_ANSWER,
            sources=[],
            provider="extractive",
            notice="No matching evidence was found in the selected sources.",
        )

    notice: str | None = None
    client_for_repair = None

    # 2. Generate, degrading instead of failing when the provider misbehaves.
    try:
        if generator is not None:
            answerer, provider = generator, "custom"
        else:
            configured = _configured_client()
            if configured is None:
                answerer, provider = ExtractiveAnswerer(), "extractive"
            else:
                client_for_repair, provider = configured
                answerer = GeminiAnswerer(client_for_repair)
        answer = answerer.generate(question, evidence)
    except ProviderError as exc:
        logger.warning("LLM provider unavailable, falling back to extractive: %s", exc)
        answer = ExtractiveAnswerer().generate(question, evidence)
        provider = "extractive"
        notice = f"The AI provider was unavailable ({exc}). This answer is an extract of the indexed sources."

    # 3. Give a model one constrained repair attempt for citation drift. The
    #    final gate below is still authoritative if the repair is not clean.
    def _clean(value: str) -> bool:
        return citations_are_valid(value, evidence_numbers) and (
            not evidence_numbers or value.strip() == UNVERIFIED_ANSWER or bool(extract_citations(value))
        )

    if not _clean(answer) and client_for_repair is not None:
        try:
            repaired = client_for_repair.generate(
                "You are a citation editor. Follow the rewrite instruction exactly and add no facts.",
                build_repair_prompt(question, format_context(evidence), answer, evidence_numbers),
            )
            if _clean(repaired):
                answer = repaired
        except ProviderError as exc:
            logger.warning("Citation repair unavailable, using extractive answer: %s", exc)

    if not _clean(answer):
        logger.warning("Discarding answer with missing or invalid evidence citations")
        answer = ExtractiveAnswerer().generate(question, evidence)
        provider = "extractive"
        notice = "The answer was reduced to a verified extract of the retrieved sources."

    sources = [
        SourceRef(
            number=item.number,
            source_url=item.source_url,
            document_id=UUID(item.document_id),
            chunk_id=UUID(item.chunk_id),
            text=item.text,
            title=item.title,
            source_type=item.source_type,
        )
        for item in evidence
    ]
    return ChatResponse(answer=answer, sources=sources, provider=provider, notice=notice)
