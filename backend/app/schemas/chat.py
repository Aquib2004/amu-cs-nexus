# chat.py - schema for the grounded Q&A (RAG) endpoint.

from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)


class SourceRef(BaseModel):
    number: int
    source_url: str
    document_id: UUID
    chunk_id: UUID
    text: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceRef]
