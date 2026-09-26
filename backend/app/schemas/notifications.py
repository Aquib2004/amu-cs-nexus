from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class PushSubscriptionCreate(BaseModel):
    endpoint: HttpUrl
    keys: dict[str, str] = Field(min_length=2, max_length=2)

    @property
    def p256dh(self) -> str:
        return self.keys["p256dh"]

    @property
    def auth(self) -> str:
        return self.keys["auth"]


class PushSubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    active: bool
    created_at: datetime
    last_seen_at: datetime


class VapidPublicKey(BaseModel):
    enabled: bool
    public_key: str | None = None


class SubscriptionDeleteResponse(BaseModel):
    deleted: bool = True
    message: str = "Notifications disabled for this browser."
