# Pydantic schema for laboratories (response contract).

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LaboratoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    file: str | None
    source_url: str