# ORM model for departmental laboratories / facilities.
# Data source: the official AMU department API (important-laboratories page).

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Laboratory(Base):
    __tablename__ = "laboratories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    file: Mapped[str | None] = mapped_column(String(1000))
    source_url: Mapped[str] = mapped_column(String(1000))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    crawl_timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    content_hash: Mapped[str | None] = mapped_column(String(64))