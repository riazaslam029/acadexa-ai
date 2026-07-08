from sqlalchemy.orm import Session

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate


def create_note(
    db: Session,
    note: NoteCreate,
    owner_id: int,
):
    db_note = Note(
        title=note.title,
        content=note.content,
        subject=note.subject,
        owner_id=owner_id,
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    return db_note


def get_notes(
    db: Session,
    owner_id: int,
):
    return (
        db.query(Note)
        .filter(Note.owner_id == owner_id)
        .all()
    )


def get_note(
    db: Session,
    note_id: int,
    owner_id: int,
):
    return (
        db.query(Note)
        .filter(
            Note.id == note_id,
            Note.owner_id == owner_id,
        )
        .first()
    )


def update_note(
    db: Session,
    db_note: Note,
    note: NoteUpdate,
):
    db_note.title = note.title
    db_note.content = note.content
    db_note.subject = note.subject

    db.commit()
    db.refresh(db_note)

    return db_note


def delete_note(
    db: Session,
    db_note: Note,
):
    db.delete(db_note)
    db.commit()