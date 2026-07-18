"""create job posting tables

Revision ID: 20260719_1200
Revises: 20260719_1000
Create Date: 2026-07-19 12:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260719_1200"
down_revision: str | None = "20260719_1000"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


company_size = postgresql.ENUM(
    "LARGE_ENTERPRISE",
    "MAJOR_AFFILIATE",
    "MID_SIZED",
    "SMALL_BUSINESS",
    "STARTUP",
    "PUBLIC_ORGANIZATION",
    "UNKNOWN",
    name="company_size_v2",
    create_type=False,
)
job_source_type = postgresql.ENUM("MANUAL", "URL", name="job_source_type", create_type=False)
job_posting_status = postgresql.ENUM(
    "SAVED",
    "REVIEWING",
    "INTERESTED",
    "EXCLUDED",
    "CLOSED",
    name="job_posting_status",
    create_type=False,
)
job_employment_type = postgresql.ENUM(
    "FULL_TIME",
    "CONTRACT",
    "INTERN",
    "PART_TIME",
    "FREELANCE",
    "OTHER",
    "UNKNOWN",
    name="job_employment_type",
    create_type=False,
)
job_work_type = postgresql.ENUM(
    "ONSITE", "HYBRID", "REMOTE", "UNKNOWN", name="job_work_type", create_type=False
)
job_deadline_type = postgresql.ENUM(
    "FIXED",
    "UNTIL_FILLED",
    "ONGOING",
    "UNKNOWN",
    name="job_deadline_type",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    company_size.create(bind, checkfirst=True)
    job_source_type.create(bind, checkfirst=True)
    job_posting_status.create(bind, checkfirst=True)
    job_employment_type.create(bind, checkfirst=True)
    job_work_type.create(bind, checkfirst=True)
    job_deadline_type.create(bind, checkfirst=True)

    op.create_table(
        "companies",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("normalized_name", sa.String(length=160), nullable=False),
        sa.Column("website_url", sa.String(length=500), nullable=True),
        sa.Column("industry", sa.String(length=120), nullable=True),
        sa.Column("company_size", company_size, server_default="UNKNOWN", nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("normalized_name", name="uq_companies_normalized_name"),
    )
    op.create_index("ix_companies_normalized_name", "companies", ["normalized_name"])

    op.create_table(
        "job_postings",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("company_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("position", sa.String(length=160), nullable=True),
        sa.Column("employment_type", job_employment_type, server_default="UNKNOWN", nullable=False),
        sa.Column("career_requirement", sa.String(length=300), nullable=True),
        sa.Column("education_requirement", sa.String(length=300), nullable=True),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("work_type", job_work_type, server_default="UNKNOWN", nullable=False),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column("salary_text", sa.String(length=200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("requirements", sa.Text(), nullable=True),
        sa.Column("preferred_qualifications", sa.Text(), nullable=True),
        sa.Column("benefits", sa.Text(), nullable=True),
        sa.Column("recruitment_process", sa.Text(), nullable=True),
        sa.Column("source_type", job_source_type, server_default="MANUAL", nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("source_site", sa.String(length=120), nullable=True),
        sa.Column("original_content", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline_type", job_deadline_type, server_default="UNKNOWN", nullable=False),
        sa.Column("status", job_posting_status, server_default="SAVED", nullable=False),
        sa.Column("is_favorite", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "source_url", name="uq_job_postings_user_source_url"),
        sa.UniqueConstraint("user_id", "content_hash", name="uq_job_postings_user_content_hash"),
    )
    op.create_index("ix_job_postings_user_id", "job_postings", ["user_id"])
    op.create_index("ix_job_postings_company_id", "job_postings", ["company_id"])
    op.create_index("ix_job_postings_user_status", "job_postings", ["user_id", "status"])
    op.create_index("ix_job_postings_user_deadline", "job_postings", ["user_id", "deadline_at"])
    op.create_index("ix_job_postings_user_favorite", "job_postings", ["user_id", "is_favorite"])
    op.create_index("ix_job_postings_user_source_type", "job_postings", ["user_id", "source_type"])


def downgrade() -> None:
    op.drop_index("ix_job_postings_user_source_type", table_name="job_postings")
    op.drop_index("ix_job_postings_user_favorite", table_name="job_postings")
    op.drop_index("ix_job_postings_user_deadline", table_name="job_postings")
    op.drop_index("ix_job_postings_user_status", table_name="job_postings")
    op.drop_index("ix_job_postings_company_id", table_name="job_postings")
    op.drop_index("ix_job_postings_user_id", table_name="job_postings")
    op.drop_table("job_postings")
    op.drop_index("ix_companies_normalized_name", table_name="companies")
    op.drop_table("companies")

    bind = op.get_bind()
    job_deadline_type.drop(bind, checkfirst=True)
    job_work_type.drop(bind, checkfirst=True)
    job_employment_type.drop(bind, checkfirst=True)
    job_posting_status.drop(bind, checkfirst=True)
    job_source_type.drop(bind, checkfirst=True)
    company_size.drop(bind, checkfirst=True)
