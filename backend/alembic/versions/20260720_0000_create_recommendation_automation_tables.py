"""create recommendation automation tables

Revision ID: 20260720_0000
Revises: 20260719_2300
Create Date: 2026-07-20 10:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0000"
down_revision: str | None = "20260719_2300"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _enum(name: str, values: tuple[str, ...]) -> postgresql.ENUM:
    return postgresql.ENUM(*values, name=name, create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    for name, values in {
        "recommendation_run_frequency": ("MANUAL", "DAILY", "WEEKLY"),
        "recommendation_change_type": (
            "NEW",
            "UNCHANGED",
            "SCORE_UP",
            "SCORE_DOWN",
            "GRADE_UP",
            "GRADE_DOWN",
            "REMOVED",
            "OUTDATED",
        ),
        "recommendation_change_reason": (
            "PROFILE_UPDATED",
            "JOB_UPDATED",
            "JOB_ANALYSIS_UPDATED",
            "POLICY_UPDATED",
            "FEEDBACK_CHANGED",
            "UNKNOWN",
        ),
        "recommendation_confidence": ("HIGH", "MEDIUM", "LOW"),
        "recommendation_notification_type": (
            "NEW_HIGH_SCORE_RECOMMENDATION",
            "RECOMMENDATION_SCORE_INCREASED",
            "RECOMMENDATION_GRADE_INCREASED",
            "APPLICATION_DEADLINE_APPROACHING",
            "RECOMMENDATION_BECAME_OUTDATED",
        ),
        "recommendation_notification_status": ("PENDING", "READ", "DISMISSED", "EXPIRED"),
    }.items():
        if bind.dialect.name == "postgresql":
            enum_type = postgresql.ENUM(*values, name=name)
            enum_type.create(bind, checkfirst=True)

    op.create_table(
        "job_recommendation_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("frequency", _enum("recommendation_run_frequency", ("MANUAL", "DAILY", "WEEKLY")), server_default="MANUAL", nullable=False),
        sa.Column("preferred_run_hour", sa.Integer(), server_default="9", nullable=False),
        sa.Column("timezone", sa.String(length=64), server_default="Asia/Seoul", nullable=False),
        sa.Column("minimum_score", sa.Integer(), server_default="50", nullable=False),
        sa.Column("include_jobs_without_analysis", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("exclude_applied_jobs", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("exclude_hidden_jobs", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("notify_new_recommendations", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("notify_score_changes", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_job_recommendation_settings_user_id"),
    )
    op.create_index("ix_job_recommendation_settings_next_run", "job_recommendation_settings", ["enabled", "next_run_at"])

    op.create_table(
        "job_recommendation_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("profile_hash", sa.String(length=128), nullable=False),
        sa.Column("policy_version", sa.String(length=40), nullable=False),
        sa.Column("input_job_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("recommended_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("new_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("changed_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("removed_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["job_recommendation_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_recommendation_snapshots_user_generated", "job_recommendation_snapshots", ["user_id", "generated_at"])
    op.create_index("ix_job_recommendation_snapshots_user_run", "job_recommendation_snapshots", ["user_id", "run_id"])

    op.create_table(
        "job_recommendation_snapshot_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("snapshot_id", sa.Integer(), nullable=False),
        sa.Column("recommendation_id", sa.Integer(), nullable=True),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("grade", sa.String(length=40), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("blocking_mismatch", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("change_type", _enum("recommendation_change_type", ("NEW", "UNCHANGED", "SCORE_UP", "SCORE_DOWN", "GRADE_UP", "GRADE_DOWN", "REMOVED", "OUTDATED")), nullable=False),
        sa.Column("previous_score", sa.Integer(), nullable=True),
        sa.Column("score_delta", sa.Integer(), nullable=True),
        sa.Column("previous_grade", sa.String(length=40), nullable=True),
        sa.Column("rank_delta", sa.Integer(), nullable=True),
        sa.Column("change_reason", _enum("recommendation_change_reason", ("PROFILE_UPDATED", "JOB_UPDATED", "JOB_ANALYSIS_UPDATED", "POLICY_UPDATED", "FEEDBACK_CHANGED", "UNKNOWN")), server_default="UNKNOWN", nullable=False),
        sa.Column("reason_summary", sa.JSON(), nullable=True),
        sa.Column("missing_job_fields", sa.JSON(), nullable=True),
        sa.Column("data_completeness_score", sa.Integer(), server_default="100", nullable=False),
        sa.Column("recommendation_confidence", _enum("recommendation_confidence", ("HIGH", "MEDIUM", "LOW")), server_default="HIGH", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["job_postings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recommendation_id"], ["job_recommendations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["snapshot_id"], ["job_recommendation_snapshots.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("snapshot_id", "job_id", name="uq_job_recommendation_snapshot_items_snapshot_job"),
    )
    op.create_index("ix_job_recommendation_snapshot_items_snapshot_rank", "job_recommendation_snapshot_items", ["snapshot_id", "rank"])
    op.create_index("ix_job_recommendation_snapshot_items_recommendation", "job_recommendation_snapshot_items", ["recommendation_id"])

    op.create_table(
        "recommendation_notification_candidates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recommendation_id", sa.Integer(), nullable=True),
        sa.Column("snapshot_id", sa.Integer(), nullable=False),
        sa.Column("snapshot_item_id", sa.Integer(), nullable=True),
        sa.Column("notification_type", _enum("recommendation_notification_type", ("NEW_HIGH_SCORE_RECOMMENDATION", "RECOMMENDATION_SCORE_INCREASED", "RECOMMENDATION_GRADE_INCREASED", "APPLICATION_DEADLINE_APPROACHING", "RECOMMENDATION_BECAME_OUTDATED")), nullable=False),
        sa.Column("status", _enum("recommendation_notification_status", ("PENDING", "READ", "DISMISSED", "EXPIRED")), server_default="PENDING", nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dismissed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["recommendation_id"], ["job_recommendations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["snapshot_id"], ["job_recommendation_snapshots.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["snapshot_item_id"], ["job_recommendation_snapshot_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "snapshot_id", "recommendation_id", "notification_type", name="uq_recommendation_notifications_unique_candidate"),
    )
    op.create_index("ix_recommendation_notifications_user_status", "recommendation_notification_candidates", ["user_id", "status"])
    op.create_index("ix_recommendation_notifications_user_created", "recommendation_notification_candidates", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_recommendation_notifications_user_created", table_name="recommendation_notification_candidates")
    op.drop_index("ix_recommendation_notifications_user_status", table_name="recommendation_notification_candidates")
    op.drop_table("recommendation_notification_candidates")
    op.drop_index("ix_job_recommendation_snapshot_items_recommendation", table_name="job_recommendation_snapshot_items")
    op.drop_index("ix_job_recommendation_snapshot_items_snapshot_rank", table_name="job_recommendation_snapshot_items")
    op.drop_table("job_recommendation_snapshot_items")
    op.drop_index("ix_job_recommendation_snapshots_user_run", table_name="job_recommendation_snapshots")
    op.drop_index("ix_job_recommendation_snapshots_user_generated", table_name="job_recommendation_snapshots")
    op.drop_table("job_recommendation_snapshots")
    op.drop_index("ix_job_recommendation_settings_next_run", table_name="job_recommendation_settings")
    op.drop_table("job_recommendation_settings")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for name in (
            "recommendation_notification_status",
            "recommendation_notification_type",
            "recommendation_confidence",
            "recommendation_change_reason",
            "recommendation_change_type",
            "recommendation_run_frequency",
        ):
            postgresql.ENUM(name=name).drop(bind, checkfirst=True)
