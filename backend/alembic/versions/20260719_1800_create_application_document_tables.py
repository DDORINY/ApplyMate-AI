"""create application document tables

Revision ID: 20260719_1800
Revises: 20260719_1700
Create Date: 2026-07-19 18:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260719_1800"
down_revision: str | None = "20260719_1700"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


document_type = postgresql.ENUM(
    "MOTIVATION",
    "JOB_COMPETENCY",
    "SELF_INTRODUCTION",
    "PROJECT_EXPERIENCE",
    "CAREER_EXPERIENCE",
    "FUTURE_PLAN",
    "FREE_FORM",
    "CUSTOM_QUESTION",
    name="application_document_type",
    create_type=False,
)
document_tone = postgresql.ENUM(
    "PROFESSIONAL",
    "CONCISE",
    "CONFIDENT",
    "HUMBLE",
    "TECHNICAL",
    "STORYTELLING",
    name="application_document_tone",
    create_type=False,
)
document_status = postgresql.ENUM(
    "DRAFT",
    "GENERATING",
    "COMPLETED",
    "FAILED",
    "REVIEW_REQUIRED",
    "ARCHIVED",
    name="application_document_status",
    create_type=False,
)
run_status = postgresql.ENUM(
    "PENDING",
    "PROCESSING",
    "COMPLETED",
    "FAILED",
    "INVALID_OUTPUT",
    "PROVIDER_UNAVAILABLE",
    name="generation_run_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    document_type.create(bind, checkfirst=True)
    document_tone.create(bind, checkfirst=True)
    document_status.create(bind, checkfirst=True)
    run_status.create(bind, checkfirst=True)

    op.create_table(
        "application_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=True),
        sa.Column("resume_id", sa.Integer(), nullable=True),
        sa.Column("resume_file_id", sa.Integer(), nullable=True),
        sa.Column("resume_analysis_id", sa.Integer(), nullable=True),
        sa.Column("job_analysis_id", sa.Integer(), nullable=True),
        sa.Column("job_match_id", sa.Integer(), nullable=True),
        sa.Column("document_type", document_type, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("question", sa.Text(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("tone", document_tone, server_default="PROFESSIONAL", nullable=False),
        sa.Column("language", sa.String(length=20), server_default="ko", nullable=False),
        sa.Column("character_limit", sa.Integer(), nullable=True),
        sa.Column("minimum_character_count", sa.Integer(), nullable=True),
        sa.Column("target_character_count", sa.Integer(), nullable=True),
        sa.Column("maximum_character_count", sa.Integer(), nullable=True),
        sa.Column("focus_points", sa.JSON(), nullable=False),
        sa.Column("avoid_phrases", sa.JSON(), nullable=False),
        sa.Column("settings", sa.JSON(), nullable=False),
        sa.Column("status", document_status, server_default="DRAFT", nullable=False),
        sa.Column("current_version_number", sa.Integer(), nullable=True),
        sa.Column("is_archived", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["job_analysis_id"], ["job_analyses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["job_id"], ["job_postings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["job_match_id"], ["job_matches.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resume_analysis_id"], ["resume_analyses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resume_file_id"], ["resume_files.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_application_documents_user_id", "application_documents", ["user_id"])
    op.create_index("ix_application_documents_user_status", "application_documents", ["user_id", "status"])
    op.create_index("ix_application_documents_user_type", "application_documents", ["user_id", "document_type"])
    op.create_index("ix_application_documents_user_archived", "application_documents", ["user_id", "is_archived"])
    op.create_index("ix_application_documents_job_id", "application_documents", ["job_id"])
    op.create_index("ix_application_documents_resume_id", "application_documents", ["resume_id"])

    op.create_table(
        "generation_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", run_status, server_default="PENDING", nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("prompt_version", sa.String(length=30), nullable=False),
        sa.Column("schema_version", sa.String(length=30), nullable=False),
        sa.Column("input_hash", sa.String(length=128), nullable=False),
        sa.Column("settings", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("safe_error_message", sa.String(length=500), nullable=True),
        sa.Column("usage_metadata", sa.JSON(), nullable=False),
        sa.Column("result_snapshot", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["application_documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_generation_runs_user_id", "generation_runs", ["user_id"])
    op.create_index("ix_generation_runs_document_id", "generation_runs", ["document_id"])
    op.create_index("ix_generation_runs_user_status", "generation_runs", ["user_id", "status"])
    op.create_index("ix_generation_runs_created_at", "generation_runs", ["created_at"])

    op.create_table(
        "application_document_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_blocks", sa.JSON(), nullable=False),
        sa.Column("character_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("character_count_without_spaces", sa.Integer(), server_default="0", nullable=False),
        sa.Column("word_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("paragraph_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("limit_exceeded", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_ai_generated", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_user_edited", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("generation_run_id", sa.Integer(), nullable=True),
        sa.Column("change_summary", sa.String(length=300), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["application_documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["generation_run_id"], ["generation_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", "version_number", name="uq_application_document_versions_document_version"),
    )
    op.create_index("ix_application_document_versions_user_id", "application_document_versions", ["user_id"])
    op.create_index("ix_application_document_versions_document_id", "application_document_versions", ["document_id"])

    op.create_table(
        "application_document_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.String(length=80), nullable=False),
        sa.Column("source_version", sa.String(length=80), nullable=True),
        sa.Column("source_hash", sa.String(length=128), nullable=False),
        sa.Column("field_path", sa.String(length=300), nullable=True),
        sa.Column("source_snapshot", sa.JSON(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["application_documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["version_id"], ["application_document_versions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_application_document_sources_user_id", "application_document_sources", ["user_id"])
    op.create_index("ix_application_document_sources_document_id", "application_document_sources", ["document_id"])
    op.create_index("ix_application_document_sources_version_id", "application_document_sources", ["version_id"])
    op.create_index("ix_application_document_sources_source", "application_document_sources", ["source_type", "source_id"])


def downgrade() -> None:
    op.drop_index("ix_application_document_sources_source", table_name="application_document_sources")
    op.drop_index("ix_application_document_sources_version_id", table_name="application_document_sources")
    op.drop_index("ix_application_document_sources_document_id", table_name="application_document_sources")
    op.drop_index("ix_application_document_sources_user_id", table_name="application_document_sources")
    op.drop_table("application_document_sources")
    op.drop_index("ix_application_document_versions_document_id", table_name="application_document_versions")
    op.drop_index("ix_application_document_versions_user_id", table_name="application_document_versions")
    op.drop_table("application_document_versions")
    op.drop_index("ix_generation_runs_created_at", table_name="generation_runs")
    op.drop_index("ix_generation_runs_user_status", table_name="generation_runs")
    op.drop_index("ix_generation_runs_document_id", table_name="generation_runs")
    op.drop_index("ix_generation_runs_user_id", table_name="generation_runs")
    op.drop_table("generation_runs")
    op.drop_index("ix_application_documents_resume_id", table_name="application_documents")
    op.drop_index("ix_application_documents_job_id", table_name="application_documents")
    op.drop_index("ix_application_documents_user_archived", table_name="application_documents")
    op.drop_index("ix_application_documents_user_type", table_name="application_documents")
    op.drop_index("ix_application_documents_user_status", table_name="application_documents")
    op.drop_index("ix_application_documents_user_id", table_name="application_documents")
    op.drop_table("application_documents")
    bind = op.get_bind()
    run_status.drop(bind, checkfirst=True)
    document_status.drop(bind, checkfirst=True)
    document_tone.drop(bind, checkfirst=True)
    document_type.drop(bind, checkfirst=True)
