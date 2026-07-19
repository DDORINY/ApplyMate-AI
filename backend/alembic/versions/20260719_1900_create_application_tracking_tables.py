"""create application tracking tables

Revision ID: 20260719_1900
Revises: 20260719_1800
Create Date: 2026-07-19 19:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260719_1900"
down_revision: str | None = "20260719_1800"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


application_status = postgresql.ENUM(
    "SAVED",
    "PREPARING",
    "APPLIED",
    "DOCUMENT_REVIEW",
    "CODING_TEST",
    "ASSIGNMENT",
    "INTERVIEW",
    "FINAL_INTERVIEW",
    "OFFER",
    "REJECTED",
    "WITHDRAWN",
    "CLOSED",
    name="application_status",
    create_type=False,
)
application_channel = postgresql.ENUM(
    "COMPANY_SITE",
    "JOB_PORTAL",
    "EMAIL",
    "REFERRAL",
    "RECRUITER",
    "TALENT_POOL",
    "OFFLINE",
    "OTHER",
    name="application_channel",
    create_type=False,
)
application_priority = postgresql.ENUM(
    "LOW",
    "NORMAL",
    "HIGH",
    "URGENT",
    name="application_priority",
    create_type=False,
)
history_source = postgresql.ENUM(
    "USER",
    "SYSTEM",
    "EMAIL_CANDIDATE",
    "CALENDAR_SYNC",
    name="application_status_history_source",
    create_type=False,
)
note_type = postgresql.ENUM(
    "GENERAL",
    "CONTACT",
    "INTERVIEW",
    "DOCUMENT",
    "RESULT",
    "REMINDER",
    name="application_note_type",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    application_status.create(bind, checkfirst=True)
    application_channel.create(bind, checkfirst=True)
    application_priority.create(bind, checkfirst=True)
    history_source.create(bind, checkfirst=True)
    note_type.create(bind, checkfirst=True)

    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=True),
        sa.Column("resume_id", sa.Integer(), nullable=True),
        sa.Column("resume_file_id", sa.Integer(), nullable=True),
        sa.Column("application_document_id", sa.Integer(), nullable=True),
        sa.Column("application_document_version_id", sa.Integer(), nullable=True),
        sa.Column("status", application_status, server_default="SAVED", nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_apply_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("application_channel", application_channel, server_default="COMPANY_SITE", nullable=False),
        sa.Column("application_url", sa.String(length=1000), nullable=True),
        sa.Column("contact_name", sa.String(length=120), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("contact_phone", sa.String(length=80), nullable=True),
        sa.Column("source", sa.String(length=120), nullable=True),
        sa.Column("priority", application_priority, server_default="NORMAL", nullable=False),
        sa.Column("result_announced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("company_name_snapshot", sa.String(length=160), nullable=True),
        sa.Column("job_title_snapshot", sa.String(length=200), nullable=True),
        sa.Column("job_url_snapshot", sa.String(length=1000), nullable=True),
        sa.Column("is_archived", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["application_document_id"], ["application_documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["application_document_version_id"], ["application_document_versions.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["job_id"], ["job_postings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resume_file_id"], ["resume_files.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_applications_user_id", "applications", ["user_id"])
    op.create_index("ix_applications_user_status", "applications", ["user_id", "status"])
    op.create_index("ix_applications_user_applied_at", "applications", ["user_id", "applied_at"])
    op.create_index("ix_applications_user_updated_at", "applications", ["user_id", "updated_at"])
    op.create_index("ix_applications_user_archived", "applications", ["user_id", "is_archived"])
    op.create_index("ix_applications_job_id", "applications", ["job_id"])

    op.create_table(
        "application_status_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("previous_status", application_status, nullable=True),
        sa.Column("new_status", application_status, nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("reason", sa.String(length=300), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("source", history_source, server_default="USER", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_application_status_history_application_created",
        "application_status_history",
        ["application_id", "created_at"],
    )
    op.create_index("ix_application_status_history_user_id", "application_status_history", ["user_id"])

    op.create_table(
        "application_notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("note_type", note_type, server_default="GENERAL", nullable=False),
        sa.Column("is_pinned", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_application_notes_application_created", "application_notes", ["application_id", "created_at"])
    op.create_index("ix_application_notes_user_id", "application_notes", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_application_notes_user_id", table_name="application_notes")
    op.drop_index("ix_application_notes_application_created", table_name="application_notes")
    op.drop_table("application_notes")
    op.drop_index("ix_application_status_history_user_id", table_name="application_status_history")
    op.drop_index("ix_application_status_history_application_created", table_name="application_status_history")
    op.drop_table("application_status_history")
    op.drop_index("ix_applications_job_id", table_name="applications")
    op.drop_index("ix_applications_user_archived", table_name="applications")
    op.drop_index("ix_applications_user_updated_at", table_name="applications")
    op.drop_index("ix_applications_user_applied_at", table_name="applications")
    op.drop_index("ix_applications_user_status", table_name="applications")
    op.drop_index("ix_applications_user_id", table_name="applications")
    op.drop_table("applications")
    bind = op.get_bind()
    note_type.drop(bind, checkfirst=True)
    history_source.drop(bind, checkfirst=True)
    application_priority.drop(bind, checkfirst=True)
    application_channel.drop(bind, checkfirst=True)
    application_status.drop(bind, checkfirst=True)
