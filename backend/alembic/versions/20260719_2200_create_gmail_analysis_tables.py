"""create gmail analysis tables

Revision ID: 20260719_2200
Revises: 20260719_2100
Create Date: 2026-07-20 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "20260719_2200"
down_revision: str | None = "20260719_2100"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE external_account_purpose ADD VALUE IF NOT EXISTS 'GMAIL'")

    op.execute("DO $$ BEGIN CREATE TYPE gmail_connection_status AS ENUM ('ACTIVE', 'REAUTH_REQUIRED', 'DISCONNECTED', 'ERROR'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE email_sync_run_status AS ENUM ('RUNNING', 'COMPLETED', 'FAILED', 'PARTIAL_FAILED'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE email_processing_status AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'IGNORED', 'REVIEW_REQUIRED'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute(
        "DO $$ BEGIN CREATE TYPE email_candidate_type AS ENUM "
        "('APPLICATION_RECEIVED', 'DOCUMENT_REVIEW', 'CODING_TEST', 'ASSIGNMENT', 'INTERVIEW', "
        "'FINAL_INTERVIEW', 'OFFER', 'REJECTED', 'WITHDRAWN', 'SCHEDULE_CHANGE', 'RECRUITER_CONTACT', 'OTHER'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.execute("DO $$ BEGIN CREATE TYPE email_candidate_status AS ENUM ('NEW', 'REVIEWED', 'APPROVED', 'REJECTED', 'APPLIED', 'EXPIRED'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE email_candidate_action_type AS ENUM ('APPROVED', 'REJECTED', 'LINKED_APPLICATION', 'STATUS_CHANGED', 'SCHEDULE_CREATED'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")

    gmail_connection_status = postgresql.ENUM("ACTIVE", "REAUTH_REQUIRED", "DISCONNECTED", "ERROR", name="gmail_connection_status", create_type=False)
    email_sync_run_status = postgresql.ENUM("RUNNING", "COMPLETED", "FAILED", "PARTIAL_FAILED", name="email_sync_run_status", create_type=False)
    email_processing_status = postgresql.ENUM("PENDING", "PROCESSING", "COMPLETED", "FAILED", "IGNORED", "REVIEW_REQUIRED", name="email_processing_status", create_type=False)
    email_candidate_type = postgresql.ENUM(
        "APPLICATION_RECEIVED",
        "DOCUMENT_REVIEW",
        "CODING_TEST",
        "ASSIGNMENT",
        "INTERVIEW",
        "FINAL_INTERVIEW",
        "OFFER",
        "REJECTED",
        "WITHDRAWN",
        "SCHEDULE_CHANGE",
        "RECRUITER_CONTACT",
        "OTHER",
        name="email_candidate_type",
        create_type=False,
    )
    email_candidate_status = postgresql.ENUM("NEW", "REVIEWED", "APPROVED", "REJECTED", "APPLIED", "EXPIRED", name="email_candidate_status", create_type=False)
    email_candidate_action_type = postgresql.ENUM(
        "APPROVED",
        "REJECTED",
        "LINKED_APPLICATION",
        "STATUS_CHANGED",
        "SCHEDULE_CREATED",
        name="email_candidate_action_type",
        create_type=False,
    )

    op.create_table(
        "gmail_oauth_states",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", postgresql.ENUM("GOOGLE", name="external_provider", create_type=False), nullable=False),
        sa.Column("state_hash", sa.String(length=128), nullable=False),
        sa.Column("redirect_path", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("state_hash"),
    )
    op.create_index("ix_gmail_oauth_states_state_hash", "gmail_oauth_states", ["state_hash"])
    op.create_index("ix_gmail_oauth_states_expires_at", "gmail_oauth_states", ["expires_at"])

    op.create_table(
        "gmail_connections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("external_account_id", sa.Integer(), nullable=False),
        sa.Column("provider", postgresql.ENUM("GOOGLE", name="external_provider", create_type=False), nullable=False),
        sa.Column("status", gmail_connection_status, server_default="ACTIVE", nullable=False),
        sa.Column("sync_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("search_query", sa.Text(), nullable=False),
        sa.Column("lookback_days", sa.Integer(), server_default="30", nullable=False),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("history_id_encrypted", sa.Text(), nullable=True),
        sa.Column("connected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("disconnected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["external_account_id"], ["external_accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gmail_connections_user_id", "gmail_connections", ["user_id"])
    op.create_index("ix_gmail_connections_external_account_id", "gmail_connections", ["external_account_id"])

    op.create_table(
        "email_sync_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("status", email_sync_run_status, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scanned_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("matched_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("candidate_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("ignored_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("history_id_before", sa.Text(), nullable=True),
        sa.Column("history_id_after", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["connection_id"], ["gmail_connections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_sync_runs_user_connection", "email_sync_runs", ["user_id", "connection_id"])

    op.create_table(
        "email_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("provider_message_id", sa.String(length=255), nullable=False),
        sa.Column("provider_thread_id", sa.String(length=255), nullable=True),
        sa.Column("sender", sa.String(length=500), nullable=False),
        sa.Column("sender_domain", sa.String(length=255), nullable=True),
        sa.Column("subject", sa.String(length=500), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("snippet", sa.Text(), nullable=True),
        sa.Column("normalized_text_hash", sa.String(length=128), nullable=False),
        sa.Column("sanitized_text", sa.Text(), nullable=True),
        sa.Column("processing_status", email_processing_status, server_default="PENDING", nullable=False),
        sa.Column("classification", sa.String(length=80), nullable=True),
        sa.Column("confidence", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["connection_id"], ["gmail_connections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("connection_id", "provider_message_id", name="uq_email_message_connection_provider"),
    )
    op.create_index("ix_email_messages_user_received", "email_messages", ["user_id", "received_at"])
    op.create_index("ix_email_messages_user_status", "email_messages", ["user_id", "processing_status"])

    op.create_table(
        "email_analysis_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("email_message_id", sa.Integer(), nullable=False),
        sa.Column("status", email_processing_status, nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("prompt_version", sa.String(length=40), server_default="v1", nullable=False),
        sa.Column("schema_version", sa.String(length=40), server_default="v1", nullable=False),
        sa.Column("input_hash", sa.String(length=128), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("safe_error_message", sa.String(length=500), nullable=True),
        sa.Column("result_snapshot", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["email_message_id"], ["email_messages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_analysis_runs_user_message", "email_analysis_runs", ["user_id", "email_message_id"])

    op.create_table(
        "email_candidates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("email_message_id", sa.Integer(), nullable=False),
        sa.Column("analysis_run_id", sa.Integer(), nullable=True),
        sa.Column("candidate_type", email_candidate_type, nullable=False),
        sa.Column("status", email_candidate_status, server_default="NEW", nullable=False),
        sa.Column("company_name", sa.String(length=160), nullable=True),
        sa.Column("job_title", sa.String(length=200), nullable=True),
        sa.Column("application_id", sa.Integer(), nullable=True),
        sa.Column("event_payload", sa.JSON(), nullable=True),
        sa.Column("status_payload", sa.JSON(), nullable=True),
        sa.Column("confidence", sa.Integer(), server_default="0", nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("requires_review", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("review_reason", sa.String(length=500), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["analysis_run_id"], ["email_analysis_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["email_message_id"], ["email_messages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_candidates_user_status", "email_candidates", ["user_id", "status"])
    op.create_index("ix_email_candidates_user_type", "email_candidates", ["user_id", "candidate_type"])
    op.create_index("ix_email_candidates_application_id", "email_candidates", ["application_id"])

    op.create_table(
        "email_candidate_actions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("action", email_candidate_action_type, nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=True),
        sa.Column("schedule_event_id", sa.Integer(), nullable=True),
        sa.Column("previous_values", sa.JSON(), nullable=True),
        sa.Column("new_values", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["candidate_id"], ["email_candidates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["schedule_event_id"], ["schedule_events.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_candidate_actions_user_candidate", "email_candidate_actions", ["user_id", "candidate_id"])


def downgrade() -> None:
    op.drop_index("ix_email_candidate_actions_user_candidate", table_name="email_candidate_actions")
    op.drop_table("email_candidate_actions")
    op.drop_index("ix_email_candidates_application_id", table_name="email_candidates")
    op.drop_index("ix_email_candidates_user_type", table_name="email_candidates")
    op.drop_index("ix_email_candidates_user_status", table_name="email_candidates")
    op.drop_table("email_candidates")
    op.drop_index("ix_email_analysis_runs_user_message", table_name="email_analysis_runs")
    op.drop_table("email_analysis_runs")
    op.drop_index("ix_email_messages_user_status", table_name="email_messages")
    op.drop_index("ix_email_messages_user_received", table_name="email_messages")
    op.drop_table("email_messages")
    op.drop_index("ix_email_sync_runs_user_connection", table_name="email_sync_runs")
    op.drop_table("email_sync_runs")
    op.drop_index("ix_gmail_connections_external_account_id", table_name="gmail_connections")
    op.drop_index("ix_gmail_connections_user_id", table_name="gmail_connections")
    op.drop_table("gmail_connections")
    op.drop_index("ix_gmail_oauth_states_expires_at", table_name="gmail_oauth_states")
    op.drop_index("ix_gmail_oauth_states_state_hash", table_name="gmail_oauth_states")
    op.drop_table("gmail_oauth_states")
    op.execute("DROP TYPE IF EXISTS email_candidate_action_type")
    op.execute("DROP TYPE IF EXISTS email_candidate_status")
    op.execute("DROP TYPE IF EXISTS email_candidate_type")
    op.execute("DROP TYPE IF EXISTS email_processing_status")
    op.execute("DROP TYPE IF EXISTS email_sync_run_status")
    op.execute("DROP TYPE IF EXISTS gmail_connection_status")
