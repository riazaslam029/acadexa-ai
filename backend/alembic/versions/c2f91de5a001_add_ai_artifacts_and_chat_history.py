"""add ai artifacts and chat history

Revision ID: c2f91de5a001
Revises: 9a5d7bef2ef3
Create Date: 2026-07-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c2f91de5a001"
down_revision: Union[str, Sequence[str], None] = "9a5d7bef2ef3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chat_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_chat_history_id"), "chat_history", ["id"], unique=False)
    op.create_index(op.f("ix_chat_history_document_id"), "chat_history", ["document_id"], unique=False)
    op.create_index(op.f("ix_chat_history_owner_id"), "chat_history", ["owner_id"], unique=False)

    op.create_table(
        "ai_artifacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("artifact_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("difficulty", sa.String(length=20), nullable=True),
        sa.Column("language", sa.String(length=20), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_artifacts_id"), "ai_artifacts", ["id"], unique=False)
    op.create_index(op.f("ix_ai_artifacts_artifact_type"), "ai_artifacts", ["artifact_type"], unique=False)
    op.create_index(op.f("ix_ai_artifacts_document_id"), "ai_artifacts", ["document_id"], unique=False)
    op.create_index(op.f("ix_ai_artifacts_owner_id"), "ai_artifacts", ["owner_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_artifacts_owner_id"), table_name="ai_artifacts")
    op.drop_index(op.f("ix_ai_artifacts_document_id"), table_name="ai_artifacts")
    op.drop_index(op.f("ix_ai_artifacts_artifact_type"), table_name="ai_artifacts")
    op.drop_index(op.f("ix_ai_artifacts_id"), table_name="ai_artifacts")
    op.drop_table("ai_artifacts")

    op.drop_index(op.f("ix_chat_history_owner_id"), table_name="chat_history")
    op.drop_index(op.f("ix_chat_history_document_id"), table_name="chat_history")
    op.drop_index(op.f("ix_chat_history_id"), table_name="chat_history")
    op.drop_table("chat_history")
