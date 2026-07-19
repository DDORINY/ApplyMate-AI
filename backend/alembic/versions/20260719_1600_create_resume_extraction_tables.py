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


def json_type() -> sa.types.TypeEngine:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return postgresql.JSONB()
    return sa.JSON()


def upgrade() -> None:
    status_enum = postgresql.ENUM(
        "PENDING",
        "PROCESSING",
        "COMPLETED",
        "FAILED",
        "TEXT_NOT_FOUND",
        "OCR_REQUIRED",
        name="resume_extraction_status",
        create_type=False,
    )
    status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "resume_file_extractions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("resume_file_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("extraction_status", status_enum, server_default="PENDING", nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("edited_text", sa.Text(), nullable=True),
        sa.Column("page_texts", json_type(), nullable=False),
        sa.Column("section_candidates", json_type(), nullable=False),
        sa.Column("page_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("character_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("input_hash", sa.String(length=128), nullable=False),
        sa.Column("is_outdated", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_user_edited", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("current_run_id", sa.Integer(), nullable=True),
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

    op.create_table(
        "resume_extraction_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("extraction_id", sa.Integer(), nullable=True),
        sa.Column("resume_file_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", status_enum, nullable=False),
        sa.Column("input_hash", sa.String(length=128), nullable=False),
        sa.Column("extractor", sa.String(length=80), nullable=False),
        sa.Column("extractor_version", sa.String(length=40), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("page_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("character_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("metadata_json", json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["extraction_id"], ["resume_file_extractions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resume_file_id"], ["resume_files.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_resume_extraction_runs_extraction_id", "resume_extraction_runs", ["extraction_id"])
    op.create_index("ix_resume_extraction_runs_resume_file_id", "resume_extraction_runs", ["resume_file_id"])
    op.create_index("ix_resume_extraction_runs_user_id", "resume_extraction_runs", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_resume_extraction_runs_user_id", table_name="resume_extraction_runs")
    op.drop_index("ix_resume_extraction_runs_resume_file_id", table_name="resume_extraction_runs")
    op.drop_index("ix_resume_extraction_runs_extraction_id", table_name="resume_extraction_runs")
    op.drop_table("resume_extraction_runs")
    op.drop_index("ix_resume_file_extractions_user_id", table_name="resume_file_extractions")
    op.drop_table("resume_file_extractions")
    sa.Enum(
        "PENDING",
        "PROCESSING",
        "COMPLETED",
        "FAILED",
        "TEXT_NOT_FOUND",
        "OCR_REQUIRED",
        name="resume_extraction_status",
    ).drop(op.get_bind(), checkfirst=True)
