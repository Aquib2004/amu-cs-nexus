# Documents endpoints: GET /api/documents, GET /api/documents/{id}

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.documents import DocumentRepository
from app.schemas.document import DocumentDetail, DocumentListItem

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentListItem])
def list_documents(
    limit: int = Query(50, ge=1, le=100),
    offset: int = 0,
    document_type: str | None = Query(None, max_length=200),
    department: str | None = Query(None, max_length=200),
    db: Session = Depends(get_db),
) -> list[DocumentListItem]:
    """List indexed document metadata (no chunk text), with optional filters."""
    return DocumentRepository(db).list_all(
        limit=limit,
        offset=offset,
        document_type=document_type,
        department=department,
    )


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
) -> DocumentDetail:
    """Return document metadata plus its text chunks, or 404."""
    repo = DocumentRepository(db)
    document = repo.get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    # Force the relationship to load for the response schema.
    return DocumentDetail.model_validate(document, from_attributes=True)