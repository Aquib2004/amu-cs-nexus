# Programs endpoint: GET /api/programs (real AMU programme data)

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.program import Program
from app.repositories.directory import DirectoryRepository
from app.schemas.program import ProgramRead

router = APIRouter(prefix="/programs", tags=["programs"])


@router.get("", response_model=list[ProgramRead])
def list_programs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = 0,
    level: str | None = Query(None, max_length=20),
    db: Session = Depends(get_db),
) -> list[ProgramRead]:
    """Return the department's academic programmes, optionally by level (ug/pg/phd)."""
    where = Program.level == level if level else None
    return DirectoryRepository(db, Program, Program.name).list_all(
        limit=limit, offset=offset, where=where
    )