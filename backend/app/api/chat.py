# Chat endpoint: POST /api/chat with a JSON body {question, limit}.
#
# Returns a source-grounded answer plus the sources it cites.

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.uploads import ChatUploadRead, UploadDeleteResponse
from app.services.uploads import (
    MAX_FILE_BYTES,
    UploadAccessError,
    UploadValidationError,
    create_upload,
    delete_upload,
)
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/uploads", response_model=ChatUploadRead, status_code=201)
async def upload_chat_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ChatUploadRead:
    data = await file.read(MAX_FILE_BYTES + 1)
    try:
        upload, token = create_upload(db, file.filename or "upload", file.content_type or "", data)
    except UploadValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ChatUploadRead(
        id=upload.id,
        access_token=token,
        filename=upload.filename,
        content_type=upload.content_type,
        size_bytes=upload.size_bytes,
        chunk_count=len(upload.chunks),
        expires_at=upload.expires_at,
    )


@router.delete("/uploads/{upload_id}", response_model=UploadDeleteResponse)
def remove_chat_file(
    upload_id: UUID,
    x_upload_token: str = Header(..., min_length=20, max_length=200),
    db: Session = Depends(get_db),
) -> UploadDeleteResponse:
    try:
        delete_upload(db, upload_id, x_upload_token)
    except UploadAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return UploadDeleteResponse()


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """Answer from official AMU data or one token-protected student upload."""
    if (payload.upload_id is None) != (payload.upload_token is None):
        raise HTTPException(status_code=422, detail="upload_id and upload_token must be provided together")
    try:
        return answer_question(
            db,
            question=payload.question,
            limit=payload.limit,
            upload_id=payload.upload_id,
            upload_token=payload.upload_token,
        )
    except UploadAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
