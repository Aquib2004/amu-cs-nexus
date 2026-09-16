# Pydantic schemas for notices (request/response contracts).

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NoticeRead(BaseModel):
    """Response shape for a single notice."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    url: str
    category: str | None
    published_at: datetime | None
