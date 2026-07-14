from fastapi import APIRouter, Depends, File, Query, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.ai_artifact import AIArtifactResponse, ArtifactGenerateRequest, DeleteResponse
from app.schemas.chat import ChatHistoryResponse, ChatRequest, ChatResponse
from app.schemas.document import DocumentResponse
from app.services.document_service import (
    ask_document_question,
    create_document_artifact,
    get_document_artifacts,
    get_document_chat_history,
    get_user_document,
    get_user_documents,
    process_uploaded_document,
    remove_artifact,
    remove_user_document,
    search_user_documents,
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
@limiter.limit(settings.AI_RATE_LIMIT)
def chat_with_document(
    request: Request,
    document_id: int,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ask_document_question(
        db=db,
        document_id=document_id,
        question=payload.question,
        owner=current_user,
    )


@router.get(
    "/{document_id}/chat/history",
    response_model=list[ChatHistoryResponse],
)
def get_chat_history(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_document_chat_history(
        db=db,
        document_id=document_id,
        owner=current_user,
    )


def _generate_artifact(
    artifact_type: str,
    request: Request,
    document_id: int,
    payload: ArtifactGenerateRequest,
    db: Session,
    current_user: User,
):
    return create_document_artifact(
        db=db,
        document_id=document_id,
        owner=current_user,
        artifact_type=artifact_type,
        count=payload.count,
        difficulty=payload.difficulty,
        language=payload.language,
    )


def _list_artifacts(
    artifact_type: str,
    document_id: int,
    db: Session,
    current_user: User,
):
    return get_document_artifacts(
        db=db,
        document_id=document_id,
        owner=current_user,
        artifact_type=artifact_type,
    )


@router.post("/{document_id}/flashcards", response_model=AIArtifactResponse)
@limiter.limit(settings.AI_RATE_LIMIT)
def generate_flashcards(
    request: Request,
    document_id: int,
    payload: ArtifactGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _generate_artifact("flashcards", request, document_id, payload, db, current_user)


@router.get("/{document_id}/flashcards", response_model=list[AIArtifactResponse])
def list_flashcards(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _list_artifacts("flashcards", document_id, db, current_user)


@router.post("/{document_id}/mcqs", response_model=AIArtifactResponse)
@limiter.limit(settings.AI_RATE_LIMIT)
def generate_mcqs(
    request: Request,
    document_id: int,
    payload: ArtifactGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _generate_artifact("mcqs", request, document_id, payload, db, current_user)


@router.get("/{document_id}/mcqs", response_model=list[AIArtifactResponse])
def list_mcqs(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _list_artifacts("mcqs", document_id, db, current_user)


@router.post("/{document_id}/key-points", response_model=AIArtifactResponse)
@limiter.limit(settings.AI_RATE_LIMIT)
def generate_key_points(
    request: Request,
    document_id: int,
    payload: ArtifactGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _generate_artifact("key_points", request, document_id, payload, db, current_user)


@router.get("/{document_id}/key-points", response_model=list[AIArtifactResponse])
def list_key_points(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _list_artifacts("key_points", document_id, db, current_user)


@router.post("/{document_id}/notes", response_model=AIArtifactResponse)
@limiter.limit(settings.AI_RATE_LIMIT)
def generate_notes(
    request: Request,
    document_id: int,
    payload: ArtifactGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _generate_artifact("study_notes", request, document_id, payload, db, current_user)


@router.get("/{document_id}/notes", response_model=list[AIArtifactResponse])
def list_notes(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _list_artifacts("study_notes", document_id, db, current_user)


@router.post("/{document_id}/quiz", response_model=AIArtifactResponse)
@limiter.limit(settings.AI_RATE_LIMIT)
def generate_quiz(
    request: Request,
    document_id: int,
    payload: ArtifactGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _generate_artifact("quizzes", request, document_id, payload, db, current_user)


@router.get("/{document_id}/quiz", response_model=list[AIArtifactResponse])
def list_quiz(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _list_artifacts("quizzes", document_id, db, current_user)


@router.post("/{document_id}/translation", response_model=AIArtifactResponse)
@limiter.limit(settings.AI_RATE_LIMIT)
def generate_translation(
    request: Request,
    document_id: int,
    payload: ArtifactGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _generate_artifact("translations", request, document_id, payload, db, current_user)


@router.get("/{document_id}/translation", response_model=list[AIArtifactResponse])
def list_translation(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _list_artifacts("translations", document_id, db, current_user)


@router.post("/{document_id}/eli5", response_model=AIArtifactResponse)
@limiter.limit(settings.AI_RATE_LIMIT)
def generate_eli5(
    request: Request,
    document_id: int,
    payload: ArtifactGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _generate_artifact("eli5", request, document_id, payload, db, current_user)


@router.get("/{document_id}/eli5", response_model=list[AIArtifactResponse])
def list_eli5(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _list_artifacts("eli5", document_id, db, current_user)


@router.post("/{document_id}/roadmap", response_model=AIArtifactResponse)
@limiter.limit(settings.AI_RATE_LIMIT)
def generate_roadmap(
    request: Request,
    document_id: int,
    payload: ArtifactGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _generate_artifact("roadmap", request, document_id, payload, db, current_user)


@router.get("/{document_id}/roadmap", response_model=list[AIArtifactResponse])
def list_roadmap(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _list_artifacts("roadmap", document_id, db, current_user)


@router.post("/{document_id}/study-plan", response_model=AIArtifactResponse)
@limiter.limit(settings.AI_RATE_LIMIT)
def generate_study_plan(
    request: Request,
    document_id: int,
    payload: ArtifactGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _generate_artifact("study_plan", request, document_id, payload, db, current_user)


@router.get("/{document_id}/study-plan", response_model=list[AIArtifactResponse])
def list_study_plan(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _list_artifacts("study_plan", document_id, db, current_user)


@router.delete("/artifacts/{artifact_id}", response_model=DeleteResponse)
def delete_artifact(
    artifact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return remove_artifact(db=db, artifact_id=artifact_id, owner=current_user)


@router.get("/search", response_model=list[DocumentResponse])
def search_documents(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return search_user_documents(db=db, owner=current_user, query=q)