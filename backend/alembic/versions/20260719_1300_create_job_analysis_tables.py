"""create job analysis tables

Revision ID: 20260719_1300
Revises: 20260719_1200
Create Date: 2026-07-19 13:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260719_1300"
down_revision: str | None = "20260719_1200"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

job_analysis_status = postgresql.ENUM(
    "PENDING",
    "PROCESSING",
    "COMPLETED",
    "FAILED",
    name="job_analysis_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    job_analysis_status.create(bind, checkfirst=True)

    op.create_table(
        "job_analyses",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("job_posting_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("status", job_analysis_status, server_default="PENDING", nullable=False),
        sa.Column("schema_version", sa.String(length=30), nullable=False),
        sa.Column("prompt_version", sa.String(length=30), nullable=False),
        sa.Column("input_hash", sa.String(length=128), nullable=False),
        sa.Column("input_length", sa.Integer(), server_default="0", nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("position_data", postgresql.JSONB(), nullable=True),
        sa.Column("responsibilities", postgresql.JSONB(), nullable=True),
        sa.Column("required_qualifications", postgresql.JSONB(), nullable=True),
        sa.Column("preferred_qualifications", postgresql.JSONB(), nullable=True),
        sa.Column("technical_skills", postgresql.JSONB(), nullable=True),
        sa.Column("experience_data", postgresql.JSONB(), nullable=True),
        sa.Column("education_data", postgresql.JSONB(), nullable=True),
        sa.Column("work_conditions", postgresql.JSONB(), nullable=True),
        sa.Column("recruitment_process", postgresql.JSONB(), nullable=True),
        sa.Column("deadline_data", postgresql.JSONB(), nullable=True),
        sa.Column("company_values", postgresql.JSONB(), nullable=True),
        sa.Column("keywords", postgresql.JSONB(), nullable=True),
        sa.Column("warnings", postgresql.JSONB(), nullable=True),
        sa.Column("confidence", postgresql.JSONB(), nullable=True),
        sa.Column("is_user_edited", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["job_posting_id"], ["job_postings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("job_posting_id", name="uq_job_analyses_job_posting_id"),
    )
    op.create_index("ix_job_analyses_user_id", "job_analyses", ["user_id"])
    op.create_index("ix_job_analyses_user_status", "job_analyses", ["user_id", "status"])

    op.create_table(
        "job_analysis_runs",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("job_posting_id", sa.BigInteger(), nullable=False),
        sa.Column("job_analysis_id", sa.BigInteger(), nullable=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("status", job_analysis_status, server_default="PROCESSING", nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("schema_version", sa.String(length=30), nullable=False),
        sa.Column("prompt_version", sa.String(length=30), nullable=False),
        sa.Column("input_hash", sa.String(length=128), nullable=False),
        sa.Column("input_length", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.String(length=120), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("raw_response", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["job_posting_id"], ["job_postings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_analysis_id"], ["job_analyses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_job_analysis_runs_user_id", "job_analysis_runs", ["user_id"])
    op.create_index(
        "ix_job_analysis_runs_job_posting_id", "job_analysis_runs", ["job_posting_id"]
    )
    op.create_index(
        "ix_job_analysis_runs_user_status", "job_analysis_runs", ["user_id", "status"]
    )
    op.create_index("ix_job_analysis_runs_created_at", "job_analysis_runs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_job_analysis_runs_created_at", table_name="job_analysis_runs")
    op.drop_index("ix_job_analysis_runs_user_status", table_name="job_analysis_runs")
    op.drop_index("ix_job_analysis_runs_job_posting_id", table_name="job_analysis_runs")
    op.drop_index("ix_job_analysis_runs_user_id", table_name="job_analysis_runs")
    op.drop_table("job_analysis_runs")
    op.drop_index("ix_job_analyses_user_status", table_name="job_analyses")
    op.drop_index("ix_job_analyses_user_id", table_name="job_analyses")
    op.drop_table("job_analyses")

    bind = op.get_bind()
    job_analysis_status.drop(bind, checkfirst=True)
