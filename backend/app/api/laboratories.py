# Laboratories endpoint: GET /api/laboratories (real AMU lab data)

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.laboratory import Laboratory
from app.repositories.directory import DirectoryRepository
from app.schemas.laboratory import LaboratoryRead

router = APIRouter(prefix="/laboratories", tags=["laboratories"])


@router.get("", response_model=list[LaboratoryRead])
def list_laboratories(
    limit: int = Query(50, ge=1, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[LaboratoryRead]:
    """Return the department's important laboratories."""
    return DirectoryRepository(db, Laboratory, Laboratory.name).list_all(
        limit=limit, offset=offset
    )