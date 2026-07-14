from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.ai_artifact import AIArtifact
    from app.models.chat_history import ChatHistory
    from app.models.document import Document
    from app.models.note import Note


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    profile_image: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    notes: Mapped[list[Note]] = relationship(
    back_populates="owner",
    cascade="all, delete-orphan",
    )

    documents: Mapped[list[Document]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    chat_messages: Mapped[list[ChatHistory]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    artifacts: Mapped[list[AIArtifact]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )