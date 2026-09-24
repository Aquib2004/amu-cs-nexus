# Pydantic schema for academic programmes (response contract).

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProgramRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    level: str | None
    intake_seats: str | None
    duration: str | None
    eligibility: str | None
    curriculum_url: str | None
    syllabus_url: str | None
    details: str | None
    source_url: str