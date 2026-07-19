"""create resume upload tables

Revision ID: 20260719_1500
Revises: 20260719_1400
Create Date: 2026-07-19 15:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260719_1500"
down_revision: str | None = "20260719_1400"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

resume_source_type = postgresql.ENUM("USER_UPLOAD", "MANUAL", name="resume_source_type", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    resume_source_type.create(bind, checkfirst=True)

    op.create_table(
        "resumes",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_type", resume_source_type, server_default="USER_UPLOAD", nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])
    op.create_index("ix_resumes_user_default", "resumes", ["user_id", "is_default"])

    op.create_table(
        "resume_files",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("resume_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=120), nullable=False),
        sa.Column("storage_path", sa.String(length=700), nullable=False),
        sa.Column("content_type", sa.String(length=160), nullable=False),
        sa.Column("file_extension", sa.String(length=20), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("file_hash", sa.String(length=128), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("stored_filename", name="uq_resume_files_stored_filename"),
        sa.UniqueConstraint("user_id", "file_hash", name="uq_resume_files_user_file_hash"),
    )
    op.create_index("ix_resume_files_resume_id", "resume_files", ["resume_id"])
    op.create_index("ix_resume_files_user_id", "resume_files", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_resume_files_user_id", table_name="resume_files")
    op.drop_index("ix_resume_files_resume_id", table_name="resume_files")
    op.drop_table("resume_files")
    op.drop_index("ix_resumes_user_default", table_name="resumes")
    op.drop_index("ix_resumes_user_id", table_name="resumes")
    op.drop_table("resumes")

    bind = op.get_bind()
    resume_source_type.drop(bind, checkfirst=True)
