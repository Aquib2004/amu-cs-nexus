# Persistence access for Faculty rows.

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.faculty import Faculty
from app.repositories.base import BaseRepository


class FacultyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self._base = BaseRepository(session, Faculty)

    def add(self, faculty: Faculty) -> Faculty:
        return self._base.add(faculty)

    def get(self, faculty_id) -> Faculty | None:
        return self._base.get(faculty_id)

    def count(self) -> int:
        return self.session.scalar(select(func.count()).select_from(Faculty)) or 0

    def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
        department: str | None = None,
    ) -> list[Faculty]:
        stmt = select(Faculty).order_by(Faculty.name)
        if department:
            stmt = stmt.where(Faculty.department == department)
        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.scalars(stmt))