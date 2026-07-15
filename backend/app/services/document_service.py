from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.ai_artifact import (
    create_ai_artifact,
    delete_ai_artifact,
    get_ai_artifact_by_id,
    list_ai_artifacts,
)
from app.crud.chat_history import create_chat_message, list_chat_messages
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
from app.services.ai_service import ai_service, AIProviderError
from app.services.file_service import (
    cleanup_temp_file,
    get_file_extension,
    save_upload_file,
    upload_file_to_cloudinary,
    validate_upload_file,
)
from app.services.pdf_service import extract_text_from_file


def process_uploaded_document(
    db: Session,
    file,
    owner: User,
) -> Document:
    validate_upload_file(file)

    # Save uploaded file
    filename, file_path = save_upload_file(file)
    extension = get_file_extension(file)

    uploaded_path = upload_file_to_cloudinary(file_path=file_path, public_id=filename)

    try:
        # Create database record
        document = create_document(
            db,
            filename=filename,
            original_name=file.filename,
            file_path=uploaded_path,
            file_size=file.size or 0,
            file_type=extension,
            owner_id=owner.id,
        )

        # Extract text from uploaded file
        extracted_text = extract_text_from_file(file_path)

        # Save extracted text
        document = update_document_text(
            db,
            document,
            extracted_text,
        )

        # Generate AI summary (best-effort; upload still succeeds if model fails)
        try:
            summary = ai_service.generate_summary(extracted_text)
        except AIProviderError:
            summary = (
                "Summary could not be generated automatically. "
                "You can still chat with and generate study material from this document."
            )

        # Save summary
        document = update_document_summary(
            db,
            document,
            summary,
        )

        return document
    finally:
        cleanup_temp_file(file_path)


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


def ask_document_question(
    db: Session,
    document_id: int,
    question: str,
    owner: User,
) -> dict[str, str]:
    document = get_user_document(
        db,
        document_id,
        owner,
    )

    answer = ai_service.chat_with_document(
        document.extracted_text,
        question,
    )

    create_chat_message(
        db,
        document_id=document.id,
        owner_id=owner.id,
        question=question,
        answer=answer,
    )

    return {
        "answer": answer,
    }


def get_document_chat_history(
    db: Session,
    document_id: int,
    owner: User,
):
    document = get_user_document(db, document_id, owner)
    return list_chat_messages(db, document.id, owner.id)


def create_document_artifact(
    db: Session,
    document_id: int,
    owner: User,
    artifact_type: str,
    count: int = 10,
    difficulty: str | None = None,
    language: str | None = None,
):
    document = get_user_document(db, document_id, owner)

    document_text = document.extracted_text or ""
    if not document_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document text is empty. Please upload a readable document.",
        )

    if artifact_type == "flashcards":
        payload = ai_service.generate_flashcards(document_text, count=count)
    elif artifact_type == "mcqs":
        payload = ai_service.generate_mcqs(document_text, count=count, difficulty=difficulty)
    elif artifact_type == "key_points":
        payload = ai_service.generate_key_points(document_text)
    elif artifact_type == "study_notes":
        payload = ai_service.generate_study_notes(document_text)
    elif artifact_type == "quizzes":
        payload = ai_service.generate_quiz(document_text, count=count, difficulty=difficulty)
    elif artifact_type == "translations":
        if not language:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="language is required for translation",
            )
        payload = ai_service.generate_translation(document_text, language=language)
    elif artifact_type == "eli5":
        payload = ai_service.generate_eli5(document_text)
    elif artifact_type == "roadmap":
        payload = ai_service.generate_roadmap(document_text)
    elif artifact_type == "study_plan":
        payload = ai_service.generate_study_plan(document_text)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported artifact type '{artifact_type}'",
        )

    return create_ai_artifact(
        db,
        artifact_type=artifact_type,
        payload=payload,
        document_id=document.id,
        owner_id=owner.id,
        difficulty=difficulty,
        language=language,
    )


def get_document_artifacts(
    db: Session,
    document_id: int,
    owner: User,
    artifact_type: str,
):
    document = get_user_document(db, document_id, owner)
    return list_ai_artifacts(db, document.id, owner.id, artifact_type)


def remove_artifact(
    db: Session,
    artifact_id: int,
    owner: User,
) -> dict[str, str]:
    artifact = get_ai_artifact_by_id(db, artifact_id)
    if artifact is None or artifact.owner_id != owner.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found.",
        )

    delete_ai_artifact(db, artifact)
    return {"message": "Artifact deleted successfully."}


def search_user_documents(
    db: Session,
    owner: User,
    query: str,
) -> list[Document]:
    query = query.strip()
    if not query:
        return []

    return (
        db.query(Document)
        .filter(Document.owner_id == owner.id)
        .filter(
            (Document.original_name.ilike(f"%{query}%"))
            | (Document.summary.ilike(f"%{query}%"))
            | (Document.extracted_text.ilike(f"%{query}%"))
        )
        .order_by(Document.created_at.desc())
        .all()
    )