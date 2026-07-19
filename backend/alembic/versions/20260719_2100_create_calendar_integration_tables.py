"""create calendar integration tables

Revision ID: 20260719_2100
Revises: 20260719_2000
Create Date: 2026-07-19 21:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260719_2100"
down_revision: str | None = "20260719_2000"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


external_provider = postgresql.ENUM("GOOGLE", name="external_provider", create_type=False)
external_account_purpose = postgresql.ENUM("CALENDAR", name="external_account_purpose", create_type=False)
calendar_sync_direction = postgresql.ENUM(
    "INTERNAL_TO_GOOGLE",
    "GOOGLE_TO_INTERNAL",
    "BIDIRECTIONAL",
    name="calendar_sync_direction",
    create_type=False,
)
calendar_connection_status = postgresql.ENUM(
    "ACTIVE",
    "REAUTH_REQUIRED",
    "DISCONNECTED",
    "ERROR",
    name="calendar_connection_status",
    create_type=False,
)
calendar_sync_status = postgresql.ENUM(
    "SYNCED",
    "PENDING",
    "CONFLICT",
    "DELETED_INTERNAL",
    "DELETED_EXTERNAL",
    "FAILED",
    name="calendar_sync_status",
    create_type=False,
)
sync_run_status = postgresql.ENUM(
    "RUNNING",
    "COMPLETED",
    "FAILED",
    "PARTIAL_FAILED",
    name="sync_run_status",
    create_type=False,
)
sync_error_code = postgresql.ENUM(
    "CALENDAR_CONNECTION_NOT_FOUND",
    "CALENDAR_PROVIDER_DISABLED",
    "CALENDAR_PROVIDER_UNAVAILABLE",
    "CALENDAR_OAUTH_STATE_INVALID",
    "CALENDAR_OAUTH_STATE_EXPIRED",
    "CALENDAR_OAUTH_CALLBACK_FAILED",
    "CALENDAR_TOKEN_ENCRYPTION_FAILED",
    "CALENDAR_TOKEN_REFRESH_FAILED",
    "CALENDAR_REAUTH_REQUIRED",
    "CALENDAR_LIST_FAILED",
    "CALENDAR_NOT_WRITABLE",
    "CALENDAR_SYNC_FAILED",
    "CALENDAR_SYNC_CONFLICT",
    "CALENDAR_MAPPING_NOT_FOUND",
    "CALENDAR_EXTERNAL_EVENT_NOT_FOUND",
    "CALENDAR_SYNC_TOKEN_EXPIRED",
    "CALENDAR_CONNECTION_FORBIDDEN",
    name="sync_error_code",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    external_provider.create(bind, checkfirst=True)
    external_account_purpose.create(bind, checkfirst=True)
    calendar_sync_direction.create(bind, checkfirst=True)
    calendar_connection_status.create(bind, checkfirst=True)
    calendar_sync_status.create(bind, checkfirst=True)
    sync_run_status.create(bind, checkfirst=True)
    sync_error_code.create(bind, checkfirst=True)

    op.create_table(
        "calendar_oauth_states",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", external_provider, nullable=False),
        sa.Column("state_hash", sa.String(length=128), nullable=False),
        sa.Column("redirect_path", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("state_hash"),
    )
    op.create_index("ix_calendar_oauth_states_state_hash", "calendar_oauth_states", ["state_hash"])
    op.create_index("ix_calendar_oauth_states_expires_at", "calendar_oauth_states", ["expires_at"])

    op.create_table(
        "external_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", external_provider, nullable=False),
        sa.Column("purpose", external_account_purpose, server_default="CALENDAR", nullable=False),
        sa.Column("provider_account_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("scopes", sa.Text(), nullable=False),
        sa.Column("access_token_encrypted", sa.Text(), nullable=False),
        sa.Column("refresh_token_encrypted", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("token_version", sa.String(length=32), server_default="v1", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("connected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("disconnected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "purpose", "provider_account_id", name="uq_external_provider_purpose_account"),
        sa.UniqueConstraint("user_id", "provider", "purpose", name="uq_external_user_provider_purpose"),
    )
    op.create_index("ix_external_accounts_user_id", "external_accounts", ["user_id"])

    op.create_table(
        "calendar_connections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("external_account_id", sa.Integer(), nullable=False),
        sa.Column("provider", external_provider, nullable=False),
        sa.Column("selected_calendar_id", sa.String(length=500), nullable=True),
        sa.Column("selected_calendar_name", sa.String(length=255), nullable=True),
        sa.Column("selected_calendar_timezone", sa.String(length=64), nullable=True),
        sa.Column("sync_direction", calendar_sync_direction, server_default="INTERNAL_TO_GOOGLE", nullable=False),
        sa.Column("sync_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_sync_token_encrypted", sa.Text(), nullable=True),
        sa.Column("status", calendar_connection_status, server_default="ACTIVE", nullable=False),
        sa.Column("connected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("disconnected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["external_account_id"], ["external_accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_calendar_connections_user_id", "calendar_connections", ["user_id"])
    op.create_index("ix_calendar_connections_external_account_id", "calendar_connections", ["external_account_id"])

    op.create_table(
        "calendar_sync_mappings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("schedule_event_id", sa.Integer(), nullable=False),
        sa.Column("external_calendar_id", sa.String(length=500), nullable=False),
        sa.Column("external_event_id", sa.String(length=500), nullable=False),
        sa.Column("external_etag", sa.String(length=255), nullable=True),
        sa.Column("external_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_internal_hash", sa.String(length=128), nullable=True),
        sa.Column("last_external_hash", sa.String(length=128), nullable=True),
        sa.Column("sync_status", calendar_sync_status, server_default="PENDING", nullable=False),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["connection_id"], ["calendar_connections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["schedule_event_id"], ["schedule_events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("connection_id", "external_event_id", name="uq_calendar_mapping_external_event"),
        sa.UniqueConstraint("connection_id", "schedule_event_id", name="uq_calendar_mapping_schedule_event"),
    )
    op.create_index("ix_calendar_sync_mappings_user_id", "calendar_sync_mappings", ["user_id"])
    op.create_index("ix_calendar_sync_mappings_schedule_event_id", "calendar_sync_mappings", ["schedule_event_id"])

    op.create_table(
        "sync_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("direction", calendar_sync_direction, nullable=False),
        sa.Column("status", sync_run_status, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("updated_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("deleted_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("skipped_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("conflict_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("sync_token_before", sa.Text(), nullable=True),
        sa.Column("sync_token_after", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["connection_id"], ["calendar_connections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sync_runs_user_connection", "sync_runs", ["user_id", "connection_id"])

    op.create_table(
        "sync_errors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=True),
        sa.Column("sync_run_id", sa.Integer(), nullable=True),
        sa.Column("mapping_id", sa.Integer(), nullable=True),
        sa.Column("error_code", sync_error_code, nullable=False),
        sa.Column("safe_message", sa.String(length=500), nullable=False),
        sa.Column("retryable", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["connection_id"], ["calendar_connections.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["mapping_id"], ["calendar_sync_mappings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sync_run_id"], ["sync_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sync_errors_user_connection", "sync_errors", ["user_id", "connection_id"])


def downgrade() -> None:
    op.drop_index("ix_sync_errors_user_connection", table_name="sync_errors")
    op.drop_table("sync_errors")
    op.drop_index("ix_sync_runs_user_connection", table_name="sync_runs")
    op.drop_table("sync_runs")
    op.drop_index("ix_calendar_sync_mappings_schedule_event_id", table_name="calendar_sync_mappings")
    op.drop_index("ix_calendar_sync_mappings_user_id", table_name="calendar_sync_mappings")
    op.drop_table("calendar_sync_mappings")
    op.drop_index("ix_calendar_connections_external_account_id", table_name="calendar_connections")
    op.drop_index("ix_calendar_connections_user_id", table_name="calendar_connections")
    op.drop_table("calendar_connections")
    op.drop_index("ix_external_accounts_user_id", table_name="external_accounts")
    op.drop_table("external_accounts")
    op.drop_index("ix_calendar_oauth_states_expires_at", table_name="calendar_oauth_states")
    op.drop_index("ix_calendar_oauth_states_state_hash", table_name="calendar_oauth_states")
    op.drop_table("calendar_oauth_states")
    bind = op.get_bind()
    sync_error_code.drop(bind, checkfirst=True)
    sync_run_status.drop(bind, checkfirst=True)
    calendar_sync_status.drop(bind, checkfirst=True)
    calendar_connection_status.drop(bind, checkfirst=True)
    calendar_sync_direction.drop(bind, checkfirst=True)
    external_account_purpose.drop(bind, checkfirst=True)
    external_provider.drop(bind, checkfirst=True)
