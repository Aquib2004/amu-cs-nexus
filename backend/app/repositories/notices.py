# Repository for notices: query and persist Notice models.

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.notice import Notice
from app.repositories.base import BaseRepository


class NoticeRepository:
    """Data-access helpers for Notice rows."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self._base = BaseRepository(session, Notice)

    def add(self, notice: Notice) -> Notice:
        return self._base.add(notice)

    def get(self, notice_id) -> Notice | None:
        return self._base.get(notice_id)

    def count(self) -> int:
        stmt = select(func.count()).select_from(Notice)
        return self.session.scalar(stmt) or 0

    def list_recent(self, limit: int = 50) -> list[Notice]:
        stmt = select(Notice).order_by(Notice.published_at.desc()).limit(limit)
        return list(self.session.scalars(stmt))
