# Pydantic schema for faculty (response contract).
#
# shape: FacultyRead   -> GET /api/faculty, GET /api/faculty/{id}

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FacultyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    title: str | None
    designation: str | None
    department: str | None
    email: str | None
    phone: str | None
    specializations: list[str]
    research_areas: list[str]
    profile_url: str | None