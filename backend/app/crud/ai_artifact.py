from sqlalchemy.orm import Session

from app.models.ai_artifact import AIArtifact


def create_ai_artifact(
    db: Session,
    artifact_type: str,
    payload: dict,
    document_id: int,
    owner_id: int,
    title: str | None = None,
    difficulty: str | None = None,
    language: str | None = None,
) -> AIArtifact:
    artifact = AIArtifact(
        artifact_type=artifact_type,
        payload=payload,
        document_id=document_id,
        owner_id=owner_id,
        title=title,
        difficulty=difficulty,
        language=language,
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


def list_ai_artifacts(
    db: Session,
    document_id: int,
    owner_id: int,
    artifact_type: str,
) -> list[AIArtifact]:
    return (
        db.query(AIArtifact)
        .filter(
            AIArtifact.document_id == document_id,
            AIArtifact.owner_id == owner_id,
            AIArtifact.artifact_type == artifact_type,
        )
        .order_by(AIArtifact.created_at.desc())
        .all()
    )


def get_ai_artifact_by_id(db: Session, artifact_id: int) -> AIArtifact | None:
    return db.query(AIArtifact).filter(AIArtifact.id == artifact_id).first()


def delete_ai_artifact(db: Session, artifact: AIArtifact) -> None:
    db.delete(artifact)
    db.commit()
