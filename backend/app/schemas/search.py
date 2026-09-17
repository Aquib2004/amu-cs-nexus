# Response schema for search results.

from uuid import UUID

from pydantic import BaseModel


class SearchResult(BaseModel):
    chunk_id: UUID
    document_id: UUID
    text: str
    source_url: str
    score: float
