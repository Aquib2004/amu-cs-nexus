# Notices endpoints.
#
# These demonstrate the full request path: HTTP request -> router ->
# repository -> database -> response schema -> JSON response.

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.notices import NoticeRepository
from app.schemas.notice import NoticeRead

router = APIRouter(prefix="/notices", tags=["notices"])


@router.get("", response_model=list[NoticeRead])
def list_notices(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[NoticeRead]:
    """Return recent notices, newest first."""
    return NoticeRepository(db).list_recent(limit=limit, offset=offset)


@router.get("/{notice_id}", response_model=NoticeRead)
def get_notice(
    notice_id: UUID,
    db: Session = Depends(get_db),
) -> NoticeRead:
    """Return a single notice by id, or 404."""
    notice = NoticeRepository(db).get(notice_id)
    if notice is None:
        raise HTTPException(status_code=404, detail="Notice not found")
    return notice
