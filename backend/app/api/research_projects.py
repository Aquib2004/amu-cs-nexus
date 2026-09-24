# Research projects endpoint: GET /api/research-projects (real AMU data)

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.research_project import ResearchProject
from app.repositories.directory import DirectoryRepository
from app.schemas.research_project import ResearchProjectRead

router = APIRouter(prefix="/research-projects", tags=["research"])


@router.get("", response_model=list[ResearchProjectRead])
def list_research_projects(
    limit: int = Query(50, ge=1, le=100),
    offset: int = 0,
    status: str | None = Query(None, max_length=20),
    db: Session = Depends(get_db),
) -> list[ResearchProjectRead]:
    """Return research projects, optionally filtered by status (completed/ongoing)."""
    where = ResearchProject.status == status if status else None
    return DirectoryRepository(db, ResearchProject, ResearchProject.title).list_all(
        limit=limit, offset=offset, where=where
    )