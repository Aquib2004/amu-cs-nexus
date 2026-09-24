# Pydantic schema for research projects (response contract).

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ResearchProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    status: str | None
    funding_agency: str | None
    amount: str | None
    principal_investigator: str | None
    co_investigators: str | None
    description: str | None
    source_url: str