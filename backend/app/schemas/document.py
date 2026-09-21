# Pydantic schemas for documents.
#
# DocumentListItem -> GET /api/documents            (metadata only)
# DocumentDetail   -> GET /api/documents/{id}       (metadata + chunks/text)

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    source_type: str | None
    document_type: str | None
    department: str | None
    status: str


class ChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    chunk_index: int
    text: str
    page_number: int | None


class DocumentDetail(DocumentListItem):
    source_url: str
    publication_date: date | None
    updated_at: datetime | None
    chunks: list[ChunkRead]