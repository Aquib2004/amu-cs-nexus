# Repository for documents: query and persist Document models.

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository:
    """Data-access helpers for Document rows."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self._base = BaseRepository(session, Document)

    def add(self, document: Document) -> Document:
        return self._base.add(document)

    def get(self, document_id) -> Document | None:
        return self._base.get(document_id)

    def count(self) -> int:
        stmt = select(func.count()).select_from(Document)
        return self.session.scalar(stmt) or 0

    def list_all(self, limit: int = 50, offset: int = 0) -> list[Document]:
        stmt = (
            select(Document)
            .order_by(Document.crawl_timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.scalars(stmt))
