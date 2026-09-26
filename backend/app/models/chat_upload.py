# ORM models for private, expiring student-upload knowledge sources.

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.vector import VectorType


class ChatUpload(Base):
    """Extracted text from one student file, never added to the public corpus.

    The original binary is not retained. A random access token is stored only as
    a SHA-256 hash, and all access requires the matching bearer token.
    """

    __tablename__ = "chat_uploads"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    access_token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(150))
    size_bytes: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="ready")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(hours=24)
    )

    chunks: Mapped[list["ChatUploadChunk"]] = relationship(
        back_populates="upload", cascade="all, delete-orphan"
    )


class ChatUploadChunk(Base):
    __tablename__ = "chat_upload_chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    upload_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chat_uploads.id", ondelete="CASCADE"), index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    page_number: Mapped[int | None] = mapped_column(Integer)
    embedding: Mapped[list[float] | None] = mapped_column(VectorType(), nullable=True)

    upload: Mapped[ChatUpload] = relationship(back_populates="chunks")
