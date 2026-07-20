"""create notification tables

Revision ID: 20260720_0200
Revises: 20260720_0100
Create Date: 2026-07-20 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0200"
down_revision: str | None = "20260720_0100"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


notification_event_type = postgresql.ENUM(
    "SCHEDULE_REMINDER",
    "APPLICATION_DEADLINE",
    "INTERVIEW_REMINDER",
    "ASSESSMENT_DEADLINE",
    "JOB_RECOMMENDATION_NEW",
    "JOB_RECOMMENDATION_SCORE_UP",
    "GMAIL_CANDIDATE_CREATED",
    "APPLICATION_STATUS_CHANGED",
    "DOCUMENT_IMPROVEMENT_COMPLETED",
    "DOCUMENT_IMPROVEMENT_FAILED",
    "CALENDAR_SYNC_FAILED",
    "GMAIL_SYNC_FAILED",
    "SYSTEM",
    name="notification_event_type",
    create_type=False,
)
notification_channel = postgresql.ENUM("IN_APP", "EMAIL", "PUSH", name="notification_channel", create_type=False)
notification_status = postgresql.ENUM("UNREAD", "READ", "DISMISSED", "ARCHIVED", "EXPIRED", name="notification_status", create_type=False)
notification_priority = postgresql.ENUM("LOW", "NORMAL", "HIGH", "URGENT", name="notification_priority", create_type=False)
notification_delivery_status = postgresql.ENUM(
    "PENDING",
    "PROCESSING",
    "SENT",
    "FAILED",
    "RETRY_SCHEDULED",
    "CANCELLED",
    "SKIPPED",
    name="notification_delivery_status",
    create_type=False,
)
notification_processing_task_type = postgresql.ENUM(
    "PROCESS_DUE_SCHEDULE_REMINDERS",
    "PROCESS_RECOMMENDATION_NOTIFICATION_CANDIDATES",
    "PROCESS_GMAIL_CANDIDATES",
    "PROCESS_DOCUMENT_IMPROVEMENTS",
    "PROCESS_SYNC_FAILURES",
    "PROCESS_PENDING_EMAIL_DELIVERIES",
    "RETRY_FAILED_DELIVERIES",
    "EXPIRE_OLD_NOTIFICATIONS",
    "RUN_DUE_NOTIFICATIONS",
    name="notification_processing_task_type",
    create_type=False,
)
notification_processing_run_status = postgresql.ENUM("RUNNING", "COMPLETED", "FAILED", "PARTIAL_FAILED", name="notification_processing_run_status", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        notification_event_type.create(bind, checkfirst=True)
        notification_channel.create(bind, checkfirst=True)
        notification_status.create(bind, checkfirst=True)
        notification_priority.create(bind, checkfirst=True)
        notification_delivery_status.create(bind, checkfirst=True)
        notification_processing_task_type.create(bind, checkfirst=True)
        notification_processing_run_status.create(bind, checkfirst=True)

    op.create_table(
        "notification_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("in_app_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("email_enabled", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("push_enabled", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("timezone", sa.String(length=64), server_default="Asia/Seoul", nullable=False),
        sa.Column("quiet_hours_enabled", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("quiet_hours_start", sa.Time(timezone=False), nullable=True),
        sa.Column("quiet_hours_end", sa.Time(timezone=False), nullable=True),
        sa.Column("schedule_reminder_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("application_deadline_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("recommendation_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("gmail_candidate_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("document_improvement_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("sync_error_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("default_reminder_minutes", sa.Integer(), server_default="30", nullable=False),
        sa.Column("daily_digest_enabled", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("daily_digest_hour", sa.Integer(), server_default="9", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_notification_settings_user_id"),
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("event_type", notification_event_type, nullable=False),
        sa.Column("priority", notification_priority, server_default="NORMAL", nullable=False),
        sa.Column("status", notification_status, server_default="UNREAD", nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=80), nullable=False),
        sa.Column("source_id", sa.String(length=120), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("deduplication_key", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dismissed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("deduplication_key", name="uq_notifications_deduplication_key"),
    )
    op.create_index("ix_notifications_user_status_created", "notifications", ["user_id", "status", "created_at"])
    op.create_index("ix_notifications_user_event", "notifications", ["user_id", "event_type"])
    op.create_index("ix_notifications_scheduled", "notifications", ["scheduled_for"])

    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("notification_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("channel", notification_channel, nullable=False),
        sa.Column("status", notification_delivery_status, server_default="PENDING", nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("safe_error_message", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["notification_id"], ["notifications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("notification_id", "channel", name="uq_notification_deliveries_notification_channel"),
    )
    op.create_index("ix_notification_deliveries_user_status", "notification_deliveries", ["user_id", "status"])
    op.create_index("ix_notification_deliveries_next_retry", "notification_deliveries", ["next_retry_at"])

    op.create_table(
        "notification_processing_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_type", notification_processing_task_type, nullable=False),
        sa.Column("status", notification_processing_run_status, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("sent_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failed_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("skipped_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("safe_error_message", sa.String(length=500), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notification_processing_runs_task_created", "notification_processing_runs", ["task_type", "created_at"])
    op.create_index("ix_notification_processing_runs_status", "notification_processing_runs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_notification_processing_runs_status", table_name="notification_processing_runs")
    op.drop_index("ix_notification_processing_runs_task_created", table_name="notification_processing_runs")
    op.drop_table("notification_processing_runs")
    op.drop_index("ix_notification_deliveries_next_retry", table_name="notification_deliveries")
    op.drop_index("ix_notification_deliveries_user_status", table_name="notification_deliveries")
    op.drop_table("notification_deliveries")
    op.drop_index("ix_notifications_scheduled", table_name="notifications")
    op.drop_index("ix_notifications_user_event", table_name="notifications")
    op.drop_index("ix_notifications_user_status_created", table_name="notifications")
    op.drop_table("notifications")
    op.drop_table("notification_settings")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        notification_processing_run_status.drop(bind, checkfirst=True)
        notification_processing_task_type.drop(bind, checkfirst=True)
        notification_delivery_status.drop(bind, checkfirst=True)
        notification_priority.drop(bind, checkfirst=True)
        notification_status.drop(bind, checkfirst=True)
        notification_channel.drop(bind, checkfirst=True)
        notification_event_type.drop(bind, checkfirst=True)
