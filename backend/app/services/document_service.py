from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.document import (
    create_document,
    delete_document,
    get_document_by_id,
    get_documents_by_user,
    update_document_summary,
    update_document_text,
)
from app.models.document import Document
from app.models.user import User
from app.services.ai_service import generate_summary
from app.services.file_service import save_upload_file
from app.services.pdf_service import extract_text_from_pdf


def process_uploaded_document(
    db: Session,
    file,
    owner: User,
) -> Document:
    # Save uploaded file
    filename, file_path = save_upload_file(file)

    # Create database record
    document = create_document(
        db,
        filename=filename,
        original_name=file.filename,
        file_path=file_path,
        file_size=file.size or 0,
        file_type=Path(file.filename).suffix.lower(),
        owner_id=owner.id,
    )

    # Extract text from PDF
    extracted_text = extract_text_from_pdf(file_path)

    # Save extracted text
    document = update_document_text(
        db,
        document,
        extracted_text,
    )

    # Generate AI summary
    summary = generate_summary(extracted_text)

    # Save summary
    document = update_document_summary(
        db,
        document,
        summary,
    )

    return document


def get_user_documents(
    db: Session,
    owner: User,
) -> list[Document]:
    return get_documents_by_user(
        db,
        owner.id,
    )


def get_user_document(
    db: Session,
    document_id: int,
    owner: User,
) -> Document:
    document = get_document_by_id(
        db,
        document_id,
    )

    if document is None or document.owner_id != owner.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return document


def remove_user_document(
    db: Session,
    document_id: int,
    owner: User,
) -> dict[str, str]:
    document = get_user_document(
        db,
        document_id,
        owner,
    )

    delete_document(
        db,
        document,
    )

    return {
        "message": "Document deleted successfully.",
    }