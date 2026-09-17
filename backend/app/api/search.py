# Search endpoint: GET /api/search?q=&limit=&department=&document_type=

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.search import SearchResult
from app.services.search import search_chunks

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[SearchResult])
def search(
    q: str = Query(..., min_length=1, max_length=300),
    limit: int = Query(10, ge=1, le=50),
    department: str | None = Query(None, max_length=200),
    document_type: str | None = Query(None, max_length=200),
    db: Session = Depends(get_db),
) -> list[SearchResult]:
    return search_chunks(
        db,
        query=q,
        limit=limit,
        department=department,
        document_type=document_type,
    )
