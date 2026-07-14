from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.ai_artifact import AIArtifact
from app.models.document import Document
from app.models.user import User
from app.schemas.user import UserPasswordChange, UserUpdate


def update_user_profile(db: Session, user: User, payload: UserUpdate) -> User:
    if payload.name is not None:
        user.name = payload.name

    if payload.profile_image is not None:
        user.profile_image = payload.profile_image

    db.commit()
    db.refresh(user)
    return user


def change_user_password(db: Session, user: User, payload: UserPasswordChange) -> None:
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    user.hashed_password = hash_password(payload.new_password)
    db.commit()


def delete_user_account(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


def get_user_dashboard(db: Session, user: User) -> dict:
    total_documents = db.query(func.count(Document.id)).filter(Document.owner_id == user.id).scalar() or 0
    total_flashcards = (
        db.query(func.count(AIArtifact.id))
        .filter(AIArtifact.owner_id == user.id, AIArtifact.artifact_type == "flashcards")
        .scalar()
        or 0
    )
    total_quizzes = (
        db.query(func.count(AIArtifact.id))
        .filter(AIArtifact.owner_id == user.id, AIArtifact.artifact_type == "quizzes")
        .scalar()
        or 0
    )
    total_mcqs = (
        db.query(func.count(AIArtifact.id))
        .filter(AIArtifact.owner_id == user.id, AIArtifact.artifact_type == "mcqs")
        .scalar()
        or 0
    )

    total_ai_requests = (
        db.query(func.count(AIArtifact.id))
        .filter(AIArtifact.owner_id == user.id)
        .scalar()
        or 0
    )

    storage_used = db.query(func.coalesce(func.sum(Document.file_size), 0)).filter(Document.owner_id == user.id).scalar() or 0

    recent_uploads = (
        db.query(Document)
        .filter(Document.owner_id == user.id)
        .order_by(Document.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "stats": {
            "total_documents": total_documents,
            "total_flashcards": total_flashcards,
            "total_quizzes": total_quizzes,
            "total_mcqs": total_mcqs,
            "total_ai_requests": total_ai_requests,
            "storage_used_bytes": storage_used,
        },
        "recent_uploads": [
            {
                "id": doc.id,
                "original_name": doc.original_name,
                "created_at": doc.created_at,
                "file_size": doc.file_size,
                "processing_status": doc.processing_status,
            }
            for doc in recent_uploads
        ],
    }
