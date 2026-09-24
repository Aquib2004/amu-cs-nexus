# Pydantic schema for non-teaching staff (response contract).

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StaffRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    designation: str | None
    email: str | None
    phone: str | None
    image_url: str | None
    profile_url: str | None