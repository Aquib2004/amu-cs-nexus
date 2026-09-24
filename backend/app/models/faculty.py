# ORM model for faculty members.
#
# Faculty directory records (names, titles, research areas). The official AMU
# department page is the source of truth for production; these rows are seeded
# locally for development until crawling of the department site is enabled.

import uuid

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Faculty(Base):
    __tablename__ = "faculties"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    title: Mapped[str | None] = mapped_column(String(100))
    designation: Mapped[str | None] = mapped_column(String(100))
    department: Mapped[str | None] = mapped_column(String(200), default="computer-science")
    email: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(50))
    specializations: Mapped[list[str]] = mapped_column(JSON, default=list)
    research_areas: Mapped[list[str]] = mapped_column(JSON, default=list)
    profile_url: Mapped[str | None] = mapped_column(String(1000))
    image_url: Mapped[str | None] = mapped_column(String(1000))
    source_url: Mapped[str] = mapped_column(String(1000), default="")