from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.exam_resource import ExamResource
from app.schemas.exam import ExamResourceRead

router = APIRouter(prefix="/exams", tags=["exams"])


@router.get("", response_model=list[ExamResourceRead])
def list_exam_resources(
    limit: int = Query(50, ge=1, le=100),
    category: str | None = Query(None, max_length=100),
    db: Session = Depends(get_db),
) -> list[ExamResource]:
    stmt = select(ExamResource).order_by(ExamResource.title)
    if category:
        stmt = stmt.where(ExamResource.category == category)
    return list(db.scalars(stmt.limit(limit)))


@router.get("/{resource_id}", response_model=ExamResourceRead)
def get_exam_resource(resource_id: UUID, db: Session = Depends(get_db)) -> ExamResource:
    resource = db.get(ExamResource, resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Exam resource not found")
    return resource
