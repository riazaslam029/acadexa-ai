from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.user import User


class AIArtifact(Base):
    __tablename__ = "ai_artifacts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)
    language: Mapped[str | None] = mapped_column(String(20), nullable=True)

    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
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

    document: Mapped[Document] = relationship(back_populates="artifacts")
    owner: Mapped[User] = relationship(back_populates="artifacts")
