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


def update_document_text(
    db: Session,
    document: Document,
    extracted_text: str,
) -> Document:
    document.extracted_text = extracted_text
    document.processing_status = "extracted"

    db.commit()
    db.refresh(document)

    return document


def update_document_summary(
    db: Session,
    document: Document,
    summary: str,
) -> Document:
    document.summary = summary
    document.processing_status = "completed"

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

def get_document_by_id(
    db: Session,
    document_id: int,
):
    return (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )


def delete_document(
    db: Session,
    document: Document,
):
    db.delete(document)
    db.commit()