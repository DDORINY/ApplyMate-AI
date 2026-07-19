"""create job match tables

Revision ID: 20260719_1400
Revises: 20260719_1300
Create Date: 2026-07-19 14:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260719_1400"
down_revision: str | None = "20260719_1300"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

job_match_status = postgresql.ENUM(
    "PENDING", "PROCESSING", "COMPLETED", "FAILED", name="job_match_status", create_type=False
)
job_match_grade = postgresql.ENUM(
    "EXCELLENT", "GOOD", "MODERATE", "LOW", "VERY_LOW", name="job_match_grade", create_type=False
)
job_match_recommendation_status = postgresql.ENUM(
    "STRONGLY_RECOMMENDED",
    "RECOMMENDED",
    "CONSIDER",
    "NOT_RECOMMENDED",
    "INSUFFICIENT_DATA",
    name="job_match_recommendation_status",
    create_type=False,
)
job_match_feedback_type = postgresql.ENUM(
    "ACCURATE",
    "TOO_HIGH",
    "TOO_LOW",
    "MISSING_STRENGTH",
    "MISSING_RISK",
    "OTHER",
    name="job_match_feedback_type",
    create_type=False,
)


def score_column(name: str) -> sa.Column:
    return sa.Column(
        name,
        sa.Integer(),
        sa.CheckConstraint(f"{name} >= 0 AND {name} <= 100", name=f"ck_job_matches_{name}_range"),
        server_default="0",
        nullable=False,
    )


def upgrade() -> None:
    bind = op.get_bind()
    job_match_status.create(bind, checkfirst=True)
    job_match_grade.create(bind, checkfirst=True)
    job_match_recommendation_status.create(bind, checkfirst=True)
    job_match_feedback_type.create(bind, checkfirst=True)

    op.create_table(
        "job_matches",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("job_posting_id", sa.BigInteger(), nullable=False),
        sa.Column("job_analysis_id", sa.BigInteger(), nullable=False),
        sa.Column("status", job_match_status, server_default="PENDING", nullable=False),
        score_column("total_score"),
        sa.Column("grade", job_match_grade, server_default="VERY_LOW", nullable=False),
        sa.Column(
            "recommendation_status",
            job_match_recommendation_status,
            server_default="INSUFFICIENT_DATA",
            nullable=False,
        ),
        score_column("role_score"),
        score_column("skill_score"),
        score_column("experience_score"),
        score_column("project_score"),
        score_column("preference_score"),
        score_column("risk_score"),
        sa.Column("matched_skills", postgresql.JSONB(), nullable=True),
        sa.Column("missing_skills", postgresql.JSONB(), nullable=True),
        sa.Column("matched_projects", postgresql.JSONB(), nullable=True),
        sa.Column("strengths", postgresql.JSONB(), nullable=True),
        sa.Column("gaps", postgresql.JSONB(), nullable=True),
        sa.Column("risks", postgresql.JSONB(), nullable=True),
        sa.Column("recommendation_summary", sa.Text(), nullable=True),
        sa.Column(
            "profile_completeness",
            sa.Integer(),
            sa.CheckConstraint(
                "profile_completeness >= 0 AND profile_completeness <= 100",
                name="ck_job_matches_profile_completeness_range",
            ),
            server_default="0",
            nullable=False,
        ),
        sa.Column("profile_hash", sa.String(length=128), nullable=False),
        sa.Column("job_analysis_hash", sa.String(length=128), nullable=False),
        sa.Column("calculation_version", sa.String(length=30), nullable=False),
        sa.Column("explanation_provider", sa.String(length=30), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_posting_id"], ["job_postings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_analysis_id"], ["job_analyses.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("user_id", "job_posting_id", name="uq_job_matches_user_job"),
    )
    op.create_index("ix_job_matches_user_id", "job_matches", ["user_id"])
    op.create_index("ix_job_matches_user_grade", "job_matches", ["user_id", "grade"])
    op.create_index(
        "ix_job_matches_user_recommendation",
        "job_matches",
        ["user_id", "recommendation_status"],
    )

    op.create_table(
        "job_match_runs",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("job_match_id", sa.BigInteger(), nullable=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("job_posting_id", sa.BigInteger(), nullable=False),
        sa.Column("job_analysis_id", sa.BigInteger(), nullable=False),
        sa.Column("status", job_match_status, server_default="PROCESSING", nullable=False),
        sa.Column("profile_hash", sa.String(length=128), nullable=False),
        sa.Column("job_analysis_hash", sa.String(length=128), nullable=False),
        sa.Column("calculation_version", sa.String(length=30), nullable=False),
        sa.Column("total_score", sa.Integer(), nullable=True),
        sa.Column("result_snapshot", postgresql.JSONB(), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["job_match_id"], ["job_matches.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_posting_id"], ["job_postings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_analysis_id"], ["job_analyses.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_job_match_runs_user_id", "job_match_runs", ["user_id"])
    op.create_index("ix_job_match_runs_job_posting_id", "job_match_runs", ["job_posting_id"])
    op.create_index("ix_job_match_runs_created_at", "job_match_runs", ["created_at"])

    op.create_table(
        "job_match_feedback",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("job_match_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("feedback_type", job_match_feedback_type, nullable=False),
        sa.Column(
            "rating",
            sa.Integer(),
            sa.CheckConstraint(
                "(rating IS NULL) OR (rating >= 1 AND rating <= 5)",
                name="ck_job_match_feedback_rating_range",
            ),
            nullable=True,
        ),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["job_match_id"], ["job_matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_job_match_feedback_user_match", "job_match_feedback", ["user_id", "job_match_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_job_match_feedback_user_match", table_name="job_match_feedback")
    op.drop_table("job_match_feedback")
    op.drop_index("ix_job_match_runs_created_at", table_name="job_match_runs")
    op.drop_index("ix_job_match_runs_job_posting_id", table_name="job_match_runs")
    op.drop_index("ix_job_match_runs_user_id", table_name="job_match_runs")
    op.drop_table("job_match_runs")
    op.drop_index("ix_job_matches_user_recommendation", table_name="job_matches")
    op.drop_index("ix_job_matches_user_grade", table_name="job_matches")
    op.drop_index("ix_job_matches_user_id", table_name="job_matches")
    op.drop_table("job_matches")

    bind = op.get_bind()
    job_match_feedback_type.drop(bind, checkfirst=True)
    job_match_recommendation_status.drop(bind, checkfirst=True)
    job_match_grade.drop(bind, checkfirst=True)
    job_match_status.drop(bind, checkfirst=True)
