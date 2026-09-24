# ORM model for academic programmes offered by the department.
# Data source: the official AMU department API (department-list-data pages).

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(500))
    # level: ug | pg | phd
    level: Mapped[str | None] = mapped_column(String(20))
    intake_seats: Mapped[str | None] = mapped_column(String(100))
    duration: Mapped[str | None] = mapped_column(Text)
    eligibility: Mapped[str | None] = mapped_column(Text)
    curriculum_url: Mapped[str | None] = mapped_column(String(1000))
    syllabus_url: Mapped[str | None] = mapped_column(String(1000))
    details: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(String(1000))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    crawl_timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    content_hash: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), default="active")