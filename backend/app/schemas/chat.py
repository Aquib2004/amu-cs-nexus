# chat.py - request/response contract for the grounded Q&A (RAG) endpoint.
#
# These classes are the API contract: FastAPI validates the request against
# ChatRequest and serialises the response from ChatResponse. Keeping them in
# `schemas/` means the wire format is reviewable in one file.

from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """What the browser sends to POST /api/chat."""

    # min_length stops empty questions; max_length stops prompt-flooding.
    question: str = Field(..., min_length=1, max_length=500)
    # More evidence = better LLM answers. 8 works well with free-tier tokens.
    limit: int = Field(default=8, ge=1, le=20)
    # When present, this question is answered ONLY from the selected private
    # upload. The token is required and never persisted in browser storage.
    upload_id: UUID | None = None
    upload_token: str | None = Field(default=None, min_length=20, max_length=200)


class SourceRef(BaseModel):
    """One citation: the numbered evidence an answer sentence points at."""

    number: int
    source_url: str
    document_id: UUID
    chunk_id: UUID
    text: str
    title: str = "Source"
    source_type: str = "official"


class ChatResponse(BaseModel):
    """What the endpoint returns: an answer plus the sources backing it."""

    answer: str
    sources: list[SourceRef]
    # Which generator produced the answer ("gemini" or "extractive"). Exposed so
    # the UI can be honest with the user about how the answer was produced.
    provider: str = "extractive"
    # Set when the answer had to be degraded (provider down, invalid citations).
    notice: str | None = None
