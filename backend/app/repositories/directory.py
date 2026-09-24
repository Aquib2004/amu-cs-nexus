# A single generic repository for the "directory" tables that only need
# simple list-and-filter behaviour (programs, laboratories, research projects,
# non-teaching staff). Specific behaviours (documents, faculty) keep their own
# repositories.

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository


class DirectoryRepository:
    """Generic read-list persistence for a model with an order column."""

    def __init__(self, session: Session, model, order_by) -> None:
        self.session = session
        self.model = model
        self._order = order_by
        self._base = BaseRepository(session, model)

    def add(self, obj):
        return self._base.add(obj)

    def get(self, obj_id):
        return self._base.get(obj_id)

    def count(self) -> int:
        return self.session.scalar(select(func.count()).select_from(self.model)) or 0

    def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
        where=None,
    ):
        stmt = select(self.model).order_by(self._order)
        if where is not None:
            stmt = stmt.where(where)
        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.scalars(stmt))