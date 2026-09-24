# Non-teaching staff endpoint: GET /api/staff (real AMU data)

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.staff import StaffMember
from app.repositories.directory import DirectoryRepository
from app.schemas.staff import StaffRead

router = APIRouter(prefix="/staff", tags=["staff"])


@router.get("", response_model=list[StaffRead])
def list_staff(
    limit: int = Query(50, ge=1, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[StaffRead]:
    """Return the department's non-teaching staff."""
    return DirectoryRepository(db, StaffMember, StaffMember.name).list_all(
        limit=limit, offset=offset
    )