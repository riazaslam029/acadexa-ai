from sqlalchemy.orm import Session

from app.models.chat_history import ChatHistory


def create_chat_message(
    db: Session,
    document_id: int,
    owner_id: int,
    question: str,
    answer: str,
) -> ChatHistory:
    record = ChatHistory(
        document_id=document_id,
        owner_id=owner_id,
        question=question,
        answer=answer,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_chat_messages(db: Session, document_id: int, owner_id: int) -> list[ChatHistory]:
    return (
        db.query(ChatHistory)
        .filter(
            ChatHistory.document_id == document_id,
            ChatHistory.owner_id == owner_id,
        )
        .order_by(ChatHistory.created_at.asc())
        .all()
    )
