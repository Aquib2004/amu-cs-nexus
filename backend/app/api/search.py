# Search endpoint: GET /api/search?q=&limit=&department=&document_type=

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.search import SearchResult
from app.services.search import search_chunks

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[SearchResult])
def search(
    q: str,
    limit: int = 10,
    department: str | None = None,
    document_type: str | None = None,
    db: Session = Depends(get_db),
) -> list[SearchResult]:
    return search_chunks(
        db,
        query=q,
        limit=limit,
        department=department,
        document_type=document_type,
    )
