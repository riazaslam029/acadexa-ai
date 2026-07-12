from sqlalchemy.orm import Session

from app.models.document import Document


def create_document(
    db: Session,
    **kwargs,
) -> Document:
    document = Document(**kwargs)

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_documents_by_user(
    db: Session,
    owner_id: int,
):
    return (
        db.query(Document)
        .filter(Document.owner_id == owner_id)
        .all()
    )