"""create schedule tables

Revision ID: 20260719_2000
Revises: 20260719_1900
Create Date: 2026-07-19 20:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260719_2000"
down_revision: str | None = "20260719_1900"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


event_type = postgresql.ENUM(
    "APPLICATION_DEADLINE",
    "DOCUMENT_RESULT",
    "CODING_TEST",
    "ASSIGNMENT_DEADLINE",
    "INTERVIEW",
    "FINAL_INTERVIEW",
    "FINAL_RESULT",
    "OFFER_RESPONSE_DEADLINE",
    "USER_EVENT",
    name="schedule_event_type",
    create_type=False,
)
event_status = postgresql.ENUM(
    "SCHEDULED",
    "CONFIRMED",
    "COMPLETED",
    "CANCELLED",
    "MISSED",
    "TENTATIVE",
    name="schedule_event_status",
    create_type=False,
)
confidence = postgresql.ENUM(
    "CONFIRMED",
    "ESTIMATED",
    "USER_INPUT",
    "AI_EXTRACTED",
    "EMAIL_EXTRACTED",
    name="schedule_confidence",
    create_type=False,
)
reminder_type = postgresql.ENUM("IN_APP", "EMAIL", "PUSH", name="schedule_reminder_type", create_type=False)
reminder_status = postgresql.ENUM(
    "ACTIVE",
    "INACTIVE",
    "SENT",
    "FAILED",
    name="schedule_reminder_status",
    create_type=False,
)
history_action = postgresql.ENUM(
    "CREATED",
    "UPDATED",
    "STATUS_CHANGED",
    "REMINDER_CHANGED",
    "CANCELLED",
    "COMPLETED",
    "ARCHIVED",
    name="schedule_history_action",
    create_type=False,
)
history_source = postgresql.ENUM("USER", "SYSTEM", "AI", "EMAIL", name="schedule_history_source", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    event_type.create(bind, checkfirst=True)
    event_status.create(bind, checkfirst=True)
    confidence.create(bind, checkfirst=True)
    reminder_type.create(bind, checkfirst=True)
    reminder_status.create(bind, checkfirst=True)
    history_action.create(bind, checkfirst=True)
    history_source.create(bind, checkfirst=True)

    op.create_table(
        "schedule_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=True),
        sa.Column("job_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("event_type", event_type, server_default="USER_EVENT", nullable=False),
        sa.Column("status", event_status, server_default="SCHEDULED", nullable=False),
        sa.Column("confidence", confidence, server_default="USER_INPUT", nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("all_day", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("timezone", sa.String(length=64), server_default="Asia/Seoul", nullable=False),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("online_url", sa.String(length=1000), nullable=True),
        sa.Column("source", sa.String(length=120), nullable=True),
        sa.Column("source_reference", sa.String(length=500), nullable=True),
        sa.Column("is_archived", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmation_required", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["job_id"], ["job_postings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_schedule_events_user_start", "schedule_events", ["user_id", "start_at"])
    op.create_index("ix_schedule_events_user_status", "schedule_events", ["user_id", "status"])
    op.create_index("ix_schedule_events_user_type", "schedule_events", ["user_id", "event_type"])
    op.create_index("ix_schedule_events_user_archived", "schedule_events", ["user_id", "is_archived"])
    op.create_index("ix_schedule_events_application_id", "schedule_events", ["application_id"])
    op.create_index("ix_schedule_events_job_id", "schedule_events", ["job_id"])

    op.create_table(
        "schedule_reminders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("reminder_type", reminder_type, server_default="IN_APP", nullable=False),
        sa.Column("minutes_before", sa.Integer(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", reminder_status, server_default="ACTIVE", nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["schedule_events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", "reminder_type", "minutes_before", name="uq_schedule_reminders_event_type_minutes"),
    )
    op.create_index("ix_schedule_reminders_event_id", "schedule_reminders", ["event_id"])
    op.create_index("ix_schedule_reminders_user_scheduled", "schedule_reminders", ["user_id", "scheduled_at"])

    op.create_table(
        "schedule_event_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("action", history_action, nullable=False),
        sa.Column("previous_values", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("new_values", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("changed_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("source", history_source, server_default="USER", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["schedule_events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_schedule_event_history_event_created", "schedule_event_history", ["event_id", "created_at"])
    op.create_index("ix_schedule_event_history_user_id", "schedule_event_history", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_schedule_event_history_user_id", table_name="schedule_event_history")
    op.drop_index("ix_schedule_event_history_event_created", table_name="schedule_event_history")
    op.drop_table("schedule_event_history")
    op.drop_index("ix_schedule_reminders_user_scheduled", table_name="schedule_reminders")
    op.drop_index("ix_schedule_reminders_event_id", table_name="schedule_reminders")
    op.drop_table("schedule_reminders")
    op.drop_index("ix_schedule_events_job_id", table_name="schedule_events")
    op.drop_index("ix_schedule_events_application_id", table_name="schedule_events")
    op.drop_index("ix_schedule_events_user_archived", table_name="schedule_events")
    op.drop_index("ix_schedule_events_user_type", table_name="schedule_events")
    op.drop_index("ix_schedule_events_user_status", table_name="schedule_events")
    op.drop_index("ix_schedule_events_user_start", table_name="schedule_events")
    op.drop_table("schedule_events")
    bind = op.get_bind()
    history_source.drop(bind, checkfirst=True)
    history_action.drop(bind, checkfirst=True)
    reminder_status.drop(bind, checkfirst=True)
    reminder_type.drop(bind, checkfirst=True)
    confidence.drop(bind, checkfirst=True)
    event_status.drop(bind, checkfirst=True)
    event_type.drop(bind, checkfirst=True)
