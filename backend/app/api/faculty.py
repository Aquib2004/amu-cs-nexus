# Faculty endpoints: GET /api/faculty, GET /api/faculty/{id}

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.faculty import FacultyRepository
from app.schemas.faculty import FacultyRead

router = APIRouter(prefix="/faculty", tags=["faculty"])


@router.get("", response_model=list[FacultyRead])
def list_faculty(
    limit: int = Query(50, ge=1, le=100),
    offset: int = 0,
    department: str | None = Query(None, max_length=200),
    db: Session = Depends(get_db),
) -> list[FacultyRead]:
    """Return faculty, optionally filtered by department."""
    return FacultyRepository(db).list_all(
        limit=limit, offset=offset, department=department
    )


@router.get("/{faculty_id}", response_model=FacultyRead)
def get_faculty(
    faculty_id: UUID,
    db: Session = Depends(get_db),
) -> FacultyRead:
    """Return one faculty member by id, or 404."""
    member = FacultyRepository(db).get(faculty_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return member