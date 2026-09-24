# ORM model for non-teaching staff.
# Data source: the official AMU department API (non-teaching-staff page).

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StaffMember(Base):
    __tablename__ = "staff_members"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(300))
    designation: Mapped[str | None] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(100))
    image_url: Mapped[str | None] = mapped_column(String(1000))
    profile_url: Mapped[str | None] = mapped_column(String(1000))
    source_url: Mapped[str] = mapped_column(String(1000))
    crawl_timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )