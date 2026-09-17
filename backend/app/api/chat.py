# Chat endpoint: POST /api/chat with a JSON body {question, limit}.
#
# Returns a source-grounded answer plus the sources it cites.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """Answer a question using indexed evidence, with sources."""
    return answer_question(db, question=payload.question, limit=payload.limit)
