from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    application: str
    version: str
    environment: str
    database: str
