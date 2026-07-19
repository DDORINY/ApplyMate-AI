"""create resume extraction tables

Revision ID: 20260719_1600
Revises: 20260719_1500
Create Date: 2026-07-19 16:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260719_1600"
down_revision: str | None = "20260719_1500"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    status_enum = postgresql.ENUM("COMPLETED", "FAILED", name="resume_extraction_status", create_type=False)
    status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "resume_file_extractions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("resume_file_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", status_enum, nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("text_length", sa.Integer(), server_default="0", nullable=False),
        sa.Column("parser_version", sa.String(length=40), nullable=False),
        sa.Column("source_file_hash", sa.String(length=128), nullable=False),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("extracted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["resume_file_id"], ["resume_files.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("resume_file_id", name="uq_resume_file_extractions_resume_file_id"),
    )
    op.create_index("ix_resume_file_extractions_user_id", "resume_file_extractions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_resume_file_extractions_user_id", table_name="resume_file_extractions")
    op.drop_table("resume_file_extractions")
    sa.Enum("COMPLETED", "FAILED", name="resume_extraction_status").drop(op.get_bind(), checkfirst=True)
