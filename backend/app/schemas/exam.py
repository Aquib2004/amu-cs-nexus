from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExamResourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    category: str
    description: str | None
    url: str
    source_url: str
    published_at: datetime | None
