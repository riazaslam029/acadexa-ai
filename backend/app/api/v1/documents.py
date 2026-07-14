from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.document import DocumentResponse
from app.services.document_service import (
    ask_document_question,
    get_user_document,
    get_user_documents,
    process_uploaded_document,
    remove_user_document,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return process_uploaded_document(
        db=db,
        file=file,
        owner=current_user,
    )


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_documents(
        db,
        current_user,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_document(
        db,
        document_id,
        current_user,
    )


@router.delete(
    "/{document_id}",
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return remove_user_document(
        db,
        document_id,
        current_user,
    )


@router.post(
    "/{document_id}/chat",
    response_model=ChatResponse,
)
def chat_with_document(
    document_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ask_document_question(
        db=db,
        document_id=document_id,
        question=request.question,
        owner=current_user,
    )