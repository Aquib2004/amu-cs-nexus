# ORM model for research projects (ongoing / completed).
# Data source: the official AMU department API.

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ResearchProject(Base):
    __tablename__ = "research_projects"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text)
    # status: ongoing | completed
    status: Mapped[str | None] = mapped_column(String(20))
    funding_agency: Mapped[str | None] = mapped_column(String(500))
    amount: Mapped[str | None] = mapped_column(String(200))
    principal_investigator: Mapped[str | None] = mapped_column(String(300))
    co_investigators: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(String(1000))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    crawl_timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    content_hash: Mapped[str | None] = mapped_column(String(64))