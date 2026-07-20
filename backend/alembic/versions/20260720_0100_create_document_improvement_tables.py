"""create document improvement tables

Revision ID: 20260720_0100
Revises: 20260720_0000
Create Date: 2026-07-20 11:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0100"
down_revision: str | None = "20260720_0000"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _enum(name: str, values: tuple[str, ...]) -> postgresql.ENUM:
    return postgresql.ENUM(*values, name=name, create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    enum_values = {
        "document_improvement_type": (
            "CLARITY",
            "CONCISENESS",
            "PROFESSIONAL_TONE",
            "JOB_ALIGNMENT",
            "COMPANY_ALIGNMENT",
            "SKILL_EMPHASIS",
            "EXPERIENCE_EMPHASIS",
            "PROJECT_EMPHASIS",
            "ACHIEVEMENT_EMPHASIS",
            "STRUCTURE",
            "GRAMMAR",
            "LENGTH_REDUCTION",
            "LENGTH_EXPANSION",
            "CUSTOM",
        ),
        "document_improvement_run_status": (
            "PENDING",
            "PROCESSING",
            "COMPLETED",
            "FAILED",
            "INVALID_OUTPUT",
            "REVIEW_REQUIRED",
            "APPLIED",
            "REJECTED",
        ),
        "document_improvement_suggestion_status": ("PENDING", "APPROVED", "REJECTED", "APPLIED"),
        "document_improvement_change_type": ("REWRITE", "ADD", "DELETE", "STRUCTURE", "GRAMMAR", "TONE", "LENGTH"),
        "document_improvement_risk_level": ("LOW", "MEDIUM", "HIGH"),
        "document_improvement_source_type": (
            "PROFILE",
            "RESUME_TEXT",
            "RESUME_ANALYSIS",
            "JOB_POSTING",
            "JOB_ANALYSIS",
            "MATCH_ANALYSIS",
            "CURRENT_DOCUMENT",
            "USER_INSTRUCTION",
        ),
        "document_improvement_action_type": (
            "SUGGESTION_APPROVED",
            "SUGGESTION_REJECTED",
            "RUN_APPLIED",
            "RUN_REJECTED",
            "RUN_DELETED",
        ),
    }
    if bind.dialect.name == "postgresql":
        for name, values in enum_values.items():
            postgresql.ENUM(*values, name=name).create(bind, checkfirst=True)

    op.create_table(
        "document_improvement_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("application_document_id", sa.Integer(), nullable=False),
        sa.Column("base_version_id", sa.Integer(), nullable=False),
        sa.Column("result_version_id", sa.Integer(), nullable=True),
        sa.Column("status", _enum("document_improvement_run_status", enum_values["document_improvement_run_status"]), server_default="PENDING", nullable=False),
        sa.Column("improvement_type", _enum("document_improvement_type", enum_values["document_improvement_type"]), nullable=False),
        sa.Column("custom_instruction", sa.Text(), nullable=True),
        sa.Column("target_min_length", sa.Integer(), nullable=True),
        sa.Column("target_max_length", sa.Integer(), nullable=True),
        sa.Column("target_tone", sa.String(length=80), nullable=True),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("prompt_version", sa.String(length=30), nullable=False),
        sa.Column("schema_version", sa.String(length=30), nullable=False),
        sa.Column("input_hash", sa.String(length=128), nullable=False),
        sa.Column("source_hash", sa.String(length=128), nullable=False),
        sa.Column("outdated", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("safe_error_message", sa.String(length=500), nullable=True),
        sa.Column("overall_feedback", sa.Text(), nullable=True),
        sa.Column("suggested_title", sa.String(length=200), nullable=True),
        sa.Column("suggested_content", sa.Text(), nullable=True),
        sa.Column("warnings", sa.JSON(), nullable=True),
        sa.Column("missing_information", sa.JSON(), nullable=True),
        sa.Column("confidence", sa.JSON(), nullable=True),
        sa.Column("usage_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_document_id"], ["application_documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["base_version_id"], ["application_document_versions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["result_version_id"], ["application_document_versions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_document_improvement_runs_user_document", "document_improvement_runs", ["user_id", "application_document_id"])
    op.create_index("ix_document_improvement_runs_user_status", "document_improvement_runs", ["user_id", "status"])
    op.create_index("ix_document_improvement_runs_created", "document_improvement_runs", ["created_at"])

    op.create_table(
        "document_improvement_suggestions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("paragraph_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("sentence_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("original_text", sa.Text(), nullable=False),
        sa.Column("suggested_text", sa.Text(), nullable=False),
        sa.Column("change_type", _enum("document_improvement_change_type", enum_values["document_improvement_change_type"]), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("risk_level", _enum("document_improvement_risk_level", enum_values["document_improvement_risk_level"]), server_default="LOW", nullable=False),
        sa.Column("status", _enum("document_improvement_suggestion_status", enum_values["document_improvement_suggestion_status"]), server_default="PENDING", nullable=False),
        sa.Column("selected", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["document_improvement_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_document_improvement_suggestions_run", "document_improvement_suggestions", ["run_id"])
    op.create_index("ix_document_improvement_suggestions_status", "document_improvement_suggestions", ["status"])

    op.create_table(
        "document_improvement_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("source_type", _enum("document_improvement_source_type", enum_values["document_improvement_source_type"]), nullable=False),
        sa.Column("source_id", sa.String(length=80), nullable=False),
        sa.Column("source_hash", sa.String(length=128), nullable=False),
        sa.Column("source_snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["document_improvement_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_document_improvement_sources_run", "document_improvement_sources", ["run_id"])
    op.create_index("ix_document_improvement_sources_source", "document_improvement_sources", ["source_type", "source_id"])

    op.create_table(
        "document_improvement_actions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("suggestion_id", sa.Integer(), nullable=True),
        sa.Column("action", _enum("document_improvement_action_type", enum_values["document_improvement_action_type"]), nullable=False),
        sa.Column("previous_text", sa.Text(), nullable=True),
        sa.Column("new_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["document_improvement_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["suggestion_id"], ["document_improvement_suggestions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_document_improvement_actions_user_run", "document_improvement_actions", ["user_id", "run_id"])
    op.create_index("ix_document_improvement_actions_suggestion", "document_improvement_actions", ["suggestion_id"])


def downgrade() -> None:
    op.drop_index("ix_document_improvement_actions_suggestion", table_name="document_improvement_actions")
    op.drop_index("ix_document_improvement_actions_user_run", table_name="document_improvement_actions")
    op.drop_table("document_improvement_actions")
    op.drop_index("ix_document_improvement_sources_source", table_name="document_improvement_sources")
    op.drop_index("ix_document_improvement_sources_run", table_name="document_improvement_sources")
    op.drop_table("document_improvement_sources")
    op.drop_index("ix_document_improvement_suggestions_status", table_name="document_improvement_suggestions")
    op.drop_index("ix_document_improvement_suggestions_run", table_name="document_improvement_suggestions")
    op.drop_table("document_improvement_suggestions")
    op.drop_index("ix_document_improvement_runs_created", table_name="document_improvement_runs")
    op.drop_index("ix_document_improvement_runs_user_status", table_name="document_improvement_runs")
    op.drop_index("ix_document_improvement_runs_user_document", table_name="document_improvement_runs")
    op.drop_table("document_improvement_runs")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for name in (
            "document_improvement_action_type",
            "document_improvement_source_type",
            "document_improvement_risk_level",
            "document_improvement_change_type",
            "document_improvement_suggestion_status",
            "document_improvement_run_status",
            "document_improvement_type",
        ):
            postgresql.ENUM(name=name).drop(bind, checkfirst=True)
