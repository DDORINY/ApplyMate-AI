"""create job recommendation tables

Revision ID: 20260719_2300
Revises: 20260719_2200
Create Date: 2026-07-20 09:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260719_2300"
down_revision: str | Sequence[str] | None = "20260719_2200"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def create_enum(name: str, values: list[str]) -> None:
    value_sql = ", ".join(f"'{value}'" for value in values)
    op.execute(
        f"""
        DO $$
        BEGIN
            CREATE TYPE {name} AS ENUM ({value_sql});
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
        """
    )


def upgrade() -> None:
    create_enum("job_recommendation_run_status", ["PROCESSING", "COMPLETED", "FAILED"])
    create_enum("job_recommendation_grade", ["EXCELLENT", "GOOD", "POSSIBLE", "LOW", "BLOCKED"])
    create_enum("job_recommendation_status", ["ACTIVE", "OUTDATED", "HIDDEN", "ARCHIVED"])
    create_enum("job_recommendation_type", ["RULE_BASED"])
    create_enum(
        "job_recommendation_reason_type",
        [
            "ROLE_MATCH",
            "SKILL_MATCH",
            "SKILL_MISSING",
            "EXPERIENCE_MATCH",
            "EXPERIENCE_GAP",
            "EMPLOYMENT_TYPE_MATCH",
            "EMPLOYMENT_TYPE_MISMATCH",
            "LOCATION_MATCH",
            "LOCATION_MISMATCH",
            "PROJECT_MATCH",
            "PREFERENCE_MATCH",
            "DATA_INSUFFICIENT",
            "ALREADY_APPLIED",
            "USER_FEEDBACK_EXCLUDED",
        ],
    )
    create_enum(
        "job_recommendation_requirement_type",
        ["ROLE", "SKILL", "EXPERIENCE", "EMPLOYMENT_TYPE", "LOCATION", "PROJECT", "PREFERENCE", "DATA", "HISTORY"],
    )
    create_enum("job_recommendation_match_status", ["MATCHED", "MISSING", "UNKNOWN", "NOT_APPLICABLE"])
    create_enum("job_recommendation_severity", ["REQUIRED", "PREFERRED", "INFO"])
    create_enum(
        "job_recommendation_feedback_type",
        ["INTERESTED", "NOT_INTERESTED", "HIDDEN", "APPLIED", "SAVED_FOR_LATER"],
    )
    create_enum(
        "job_recommendation_feedback_reason",
        ["LOCATION", "SALARY", "ROLE", "TECH_STACK", "EXPERIENCE", "EMPLOYMENT_TYPE", "COMPANY", "OTHER"],
    )

    run_status = postgresql.ENUM("PROCESSING", "COMPLETED", "FAILED", name="job_recommendation_run_status", create_type=False)
    grade = postgresql.ENUM("EXCELLENT", "GOOD", "POSSIBLE", "LOW", "BLOCKED", name="job_recommendation_grade", create_type=False)
    rec_status = postgresql.ENUM("ACTIVE", "OUTDATED", "HIDDEN", "ARCHIVED", name="job_recommendation_status", create_type=False)
    rec_type = postgresql.ENUM("RULE_BASED", name="job_recommendation_type", create_type=False)
    reason_type = postgresql.ENUM(
        "ROLE_MATCH",
        "SKILL_MATCH",
        "SKILL_MISSING",
        "EXPERIENCE_MATCH",
        "EXPERIENCE_GAP",
        "EMPLOYMENT_TYPE_MATCH",
        "EMPLOYMENT_TYPE_MISMATCH",
        "LOCATION_MATCH",
        "LOCATION_MISMATCH",
        "PROJECT_MATCH",
        "PREFERENCE_MATCH",
        "DATA_INSUFFICIENT",
        "ALREADY_APPLIED",
        "USER_FEEDBACK_EXCLUDED",
        name="job_recommendation_reason_type",
        create_type=False,
    )
    requirement_type = postgresql.ENUM(
        "ROLE", "SKILL", "EXPERIENCE", "EMPLOYMENT_TYPE", "LOCATION", "PROJECT", "PREFERENCE", "DATA", "HISTORY",
        name="job_recommendation_requirement_type",
        create_type=False,
    )
    match_status = postgresql.ENUM("MATCHED", "MISSING", "UNKNOWN", "NOT_APPLICABLE", name="job_recommendation_match_status", create_type=False)
    severity = postgresql.ENUM("REQUIRED", "PREFERRED", "INFO", name="job_recommendation_severity", create_type=False)
    feedback_type = postgresql.ENUM("INTERESTED", "NOT_INTERESTED", "HIDDEN", "APPLIED", "SAVED_FOR_LATER", name="job_recommendation_feedback_type", create_type=False)
    feedback_reason = postgresql.ENUM(
        "LOCATION", "SALARY", "ROLE", "TECH_STACK", "EXPERIENCE", "EMPLOYMENT_TYPE", "COMPANY", "OTHER",
        name="job_recommendation_feedback_reason",
        create_type=False,
    )

    op.create_table(
        "job_recommendation_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", run_status, nullable=False, server_default="PROCESSING"),
        sa.Column("policy_version", sa.String(length=40), nullable=False),
        sa.Column("input_job_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("recommended_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("excluded_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("safe_error_message", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_job_recommendation_runs_user_created", "job_recommendation_runs", ["user_id", "created_at"])
    op.create_index("ix_job_recommendation_runs_user_status", "job_recommendation_runs", ["user_id", "status"])

    op.create_table(
        "job_recommendations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("job_recommendation_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("grade", grade, nullable=False),
        sa.Column("recommendation_type", rec_type, nullable=False, server_default="RULE_BASED"),
        sa.Column("has_blocking_mismatch", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("matched_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("missing_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unknown_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("profile_hash", sa.String(length=128), nullable=False),
        sa.Column("job_hash", sa.String(length=128), nullable=False),
        sa.Column("resume_analysis_id", sa.Integer(), sa.ForeignKey("resume_analyses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("job_analysis_id", sa.Integer(), sa.ForeignKey("job_analyses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("matching_analysis_id", sa.Integer(), sa.ForeignKey("job_matches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("policy_version", sa.String(length=40), nullable=False),
        sa.Column("input_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("score_breakdown", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("missing_profile_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("outdated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", rec_status, nullable=False, server_default="ACTIVE"),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("score >= 0 AND score <= 100", name="ck_job_recommendations_score_range"),
        sa.UniqueConstraint("user_id", "job_id", "profile_hash", "job_hash", "policy_version", name="uq_job_recommendations_user_job_snapshot_policy"),
    )
    op.create_index("ix_job_recommendations_user_score", "job_recommendations", ["user_id", "score"])
    op.create_index("ix_job_recommendations_user_grade", "job_recommendations", ["user_id", "grade"])
    op.create_index("ix_job_recommendations_user_status", "job_recommendations", ["user_id", "status"])
    op.create_index("ix_job_recommendations_user_generated", "job_recommendations", ["user_id", "generated_at"])

    op.create_table(
        "job_recommendation_reasons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recommendation_id", sa.Integer(), sa.ForeignKey("job_recommendations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason_type", reason_type, nullable=False),
        sa.Column("requirement_type", requirement_type, nullable=False),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("normalized_value", sa.String(length=160), nullable=True),
        sa.Column("match_status", match_status, nullable=False),
        sa.Column("weight", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("score_delta", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("severity", severity, nullable=False, server_default="INFO"),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_job_recommendation_reasons_recommendation", "job_recommendation_reasons", ["recommendation_id"])
    op.create_index("ix_job_recommendation_reasons_type", "job_recommendation_reasons", ["reason_type"])

    op.create_table(
        "job_recommendation_feedback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recommendation_id", sa.Integer(), sa.ForeignKey("job_recommendations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feedback_type", feedback_type, nullable=False),
        sa.Column("reason_code", feedback_reason, nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "recommendation_id", name="uq_job_recommendation_feedback_user_recommendation"),
    )
    op.create_index("ix_job_recommendation_feedback_user_recommendation", "job_recommendation_feedback", ["user_id", "recommendation_id"])


def downgrade() -> None:
    op.drop_index("ix_job_recommendation_feedback_user_recommendation", table_name="job_recommendation_feedback")
    op.drop_table("job_recommendation_feedback")
    op.drop_index("ix_job_recommendation_reasons_type", table_name="job_recommendation_reasons")
    op.drop_index("ix_job_recommendation_reasons_recommendation", table_name="job_recommendation_reasons")
    op.drop_table("job_recommendation_reasons")
    op.drop_index("ix_job_recommendations_user_generated", table_name="job_recommendations")
    op.drop_index("ix_job_recommendations_user_status", table_name="job_recommendations")
    op.drop_index("ix_job_recommendations_user_grade", table_name="job_recommendations")
    op.drop_index("ix_job_recommendations_user_score", table_name="job_recommendations")
    op.drop_table("job_recommendations")
    op.drop_index("ix_job_recommendation_runs_user_status", table_name="job_recommendation_runs")
    op.drop_index("ix_job_recommendation_runs_user_created", table_name="job_recommendation_runs")
    op.drop_table("job_recommendation_runs")

    for enum_name in [
        "job_recommendation_feedback_reason",
        "job_recommendation_feedback_type",
        "job_recommendation_severity",
        "job_recommendation_match_status",
        "job_recommendation_requirement_type",
        "job_recommendation_reason_type",
        "job_recommendation_type",
        "job_recommendation_status",
        "job_recommendation_grade",
        "job_recommendation_run_status",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
