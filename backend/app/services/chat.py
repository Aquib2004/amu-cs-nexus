# services/chat.py - grounded question answering over indexed content (RAG).
#
# Flow: retrieve relevant chunks -> structure them as numbered evidence ->
# generate an answer strictly from that evidence (ExtractiveAnswerer) ->
# expose the sources for citations. No unsupported claims are possible because
# the extractive generator only re-uses evidence text.

from uuid import UUID

from sqlalchemy.orm import Session

from ai.rag.context import build_evidence
from ai.rag.generator import AnswerGenerator, ExtractiveAnswerer
from app.schemas.chat import ChatResponse, SourceRef
from app.services.search import search_chunks


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
    answerer = generator or ExtractiveAnswerer()
    answer = answerer.generate(question, evidence)

    sources = [
        SourceRef(
            number=e.number,
            source_url=e.source_url,
            document_id=UUID(e.document_id),
            chunk_id=UUID(e.chunk_id),
            text=e.text,
        )
        for e in evidence
    ]
    return ChatResponse(answer=answer, sources=sources)
