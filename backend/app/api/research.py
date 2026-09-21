# Research endpoint: GET /api/research (documents marked as research/publication)

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.documents import DocumentRepository
from app.schemas.document import DocumentListItem

router = APIRouter(prefix="/research", tags=["research"])


@router.get("", response_model=list[DocumentListItem])
def list_research(
    limit: int = Query(20, ge=1, le=50),
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[DocumentListItem]:
    """Return documents classified as research or publication."""
    return DocumentRepository(db).list_research(limit=limit, offset=offset)