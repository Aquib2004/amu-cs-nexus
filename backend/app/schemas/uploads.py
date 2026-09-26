from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ChatUploadRead(BaseModel):
    id: UUID
    access_token: str
    filename: str
    content_type: str
    size_bytes: int
    chunk_count: int
    expires_at: datetime


class UploadDeleteResponse(BaseModel):
    deleted: bool = True
    message: str = Field(default="Upload and its indexed text were deleted.")
