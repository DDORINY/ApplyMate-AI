"""create resume analysis tables

Revision ID: 20260719_1700
Revises: 20260719_1600
Create Date: 2026-07-19 17:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260719_1700"
down_revision: str | None = "20260719_1600"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def json_type() -> sa.types.TypeEngine:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return postgresql.JSONB()
    return sa.JSON()


def status_type() -> sa.types.TypeEngine:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return postgresql.ENUM(
            "PENDING",
            "PROCESSING",
            "COMPLETED",
            "FAILED",
            "INVALID_OUTPUT",
            "PROVIDER_UNAVAILABLE",
            name="resume_analysis_status",
            create_type=False,
        )
    return sa.Enum(
        "PENDING",
        "PROCESSING",
        "COMPLETED",
        "FAILED",
        "INVALID_OUTPUT",
        "PROVIDER_UNAVAILABLE",
        name="resume_analysis_status",
    )


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        status_type().create(op.get_bind(), checkfirst=True)

    op.create_table(
        "resume_analyses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("resume_id", sa.Integer(), nullable=False),
        sa.Column("resume_file_id", sa.Integer(), nullable=False),
        sa.Column("extraction_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", status_type(), server_default="PENDING", nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=True),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("prompt_version", sa.String(length=30), nullable=False),
        sa.Column("schema_version", sa.String(length=30), nullable=False),
        sa.Column("input_hash", sa.String(length=128), nullable=False),
        sa.Column("resume_file_hash", sa.String(length=128), nullable=False),
        sa.Column("extraction_run_id", sa.Integer(), nullable=True),
        sa.Column("input_source", sa.String(length=20), nullable=False),
        sa.Column("input_length", sa.Integer(), server_default="0", nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("structured_result", json_type(), nullable=True),
        sa.Column("edited_result", json_type(), nullable=True),
        sa.Column("profile_candidates", json_type(), nullable=False),
        sa.Column("is_user_edited", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_outdated", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("latest_run_id", sa.Integer(), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["extraction_id"], ["resume_file_extractions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["resume_file_id"], ["resume_files.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("resume_file_id", name="uq_resume_analyses_resume_file_id"),
    )
    op.create_index("ix_resume_analyses_input_hash", "resume_analyses", ["input_hash"])
    op.create_index("ix_resume_analyses_resume_file_id", "resume_analyses", ["resume_file_id"])
    op.create_index("ix_resume_analyses_resume_id", "resume_analyses", ["resume_id"])
    op.create_index("ix_resume_analyses_user_id", "resume_analyses", ["user_id"])
    op.create_index("ix_resume_analyses_user_status", "resume_analyses", ["user_id", "status"])

    op.create_table(
        "resume_analysis_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("analysis_id", sa.Integer(), nullable=True),
        sa.Column("resume_id", sa.Integer(), nullable=False),
        sa.Column("resume_file_id", sa.Integer(), nullable=False),
        sa.Column("extraction_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", status_type(), server_default="PROCESSING", nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("prompt_version", sa.String(length=30), nullable=False),
        sa.Column("schema_version", sa.String(length=30), nullable=False),
        sa.Column("input_hash", sa.String(length=128), nullable=False),
        sa.Column("input_source", sa.String(length=20), nullable=False),
        sa.Column("input_length", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("result_snapshot", json_type(), nullable=True),
        sa.Column("usage_metadata", json_type(), nullable=False),
        sa.Column("raw_response_metadata", json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["resume_analyses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["extraction_id"], ["resume_file_extractions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["resume_file_id"], ["resume_files.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_resume_analysis_runs_analysis_id", "resume_analysis_runs", ["analysis_id"])
    op.create_index("ix_resume_analysis_runs_created_at", "resume_analysis_runs", ["created_at"])
    op.create_index("ix_resume_analysis_runs_input_hash", "resume_analysis_runs", ["input_hash"])
    op.create_index("ix_resume_analysis_runs_resume_file_id", "resume_analysis_runs", ["resume_file_id"])
    op.create_index("ix_resume_analysis_runs_user_id", "resume_analysis_runs", ["user_id"])
    op.create_index("ix_resume_analysis_runs_user_status", "resume_analysis_runs", ["user_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_resume_analysis_runs_user_status", table_name="resume_analysis_runs")
    op.drop_index("ix_resume_analysis_runs_user_id", table_name="resume_analysis_runs")
    op.drop_index("ix_resume_analysis_runs_resume_file_id", table_name="resume_analysis_runs")
    op.drop_index("ix_resume_analysis_runs_input_hash", table_name="resume_analysis_runs")
    op.drop_index("ix_resume_analysis_runs_created_at", table_name="resume_analysis_runs")
    op.drop_index("ix_resume_analysis_runs_analysis_id", table_name="resume_analysis_runs")
    op.drop_table("resume_analysis_runs")
    op.drop_index("ix_resume_analyses_user_status", table_name="resume_analyses")
    op.drop_index("ix_resume_analyses_user_id", table_name="resume_analyses")
    op.drop_index("ix_resume_analyses_resume_id", table_name="resume_analyses")
    op.drop_index("ix_resume_analyses_resume_file_id", table_name="resume_analyses")
    op.drop_index("ix_resume_analyses_input_hash", table_name="resume_analyses")
    op.drop_table("resume_analyses")
    sa.Enum(
        "PENDING",
        "PROCESSING",
        "COMPLETED",
        "FAILED",
        "INVALID_OUTPUT",
        "PROVIDER_UNAVAILABLE",
        name="resume_analysis_status",
    ).drop(op.get_bind(), checkfirst=True)
