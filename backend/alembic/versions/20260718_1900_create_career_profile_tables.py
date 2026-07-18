"""create career profile tables

Revision ID: 20260718_1900
Revises: 20260718_1501
Create Date: 2026-07-18 19:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260718_1900"
down_revision: str | None = "20260718_1501"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

career_level = postgresql.ENUM(
    "ENTRY", "JUNIOR", "MID", "SENIOR", "CAREER_CHANGE", name="career_level", create_type=False
)
skill_category = postgresql.ENUM(
    "LANGUAGE",
    "FRAMEWORK",
    "DATABASE",
    "AI_ML",
    "DEVOPS",
    "CLOUD",
    "FRONTEND",
    "BACKEND",
    "TOOL",
    "ETC",
    name="skill_category",
    create_type=False,
)
proficiency_level = postgresql.ENUM(
    "BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT", name="proficiency_level", create_type=False
)
employment_type = postgresql.ENUM(
    "FULL_TIME",
    "CONTRACT",
    "INTERN",
    "FREELANCE",
    "PART_TIME",
    "SELF_EMPLOYED",
    "OTHER",
    name="employment_type",
    create_type=False,
)
company_size = postgresql.ENUM(
    "LARGE_ENTERPRISE",
    "MAJOR_AFFILIATE",
    "MID_SIZED",
    "SMALL_BUSINESS",
    "STARTUP",
    "PUBLIC_ORGANIZATION",
    "ANY",
    name="company_size",
    create_type=False,
)
remote_preference = postgresql.ENUM(
    "ONSITE", "HYBRID", "REMOTE", "ANY", name="remote_preference", create_type=False
)
excluded_condition_type = postgresql.ENUM(
    "EMPLOYMENT_TYPE",
    "LOCATION",
    "COMPANY_SIZE",
    "REQUIRED_SKILL",
    "EXCLUDED_KEYWORD",
    "MINIMUM_EXPERIENCE",
    "EDUCATION_REQUIREMENT",
    "OTHER",
    name="excluded_condition_type",
    create_type=False,
)
portfolio_link_type = postgresql.ENUM(
    "GITHUB",
    "NOTION",
    "PORTFOLIO",
    "BLOG",
    "LINKEDIN",
    "OTHER",
    name="portfolio_link_type",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    for enum_type in [
        career_level,
        skill_category,
        proficiency_level,
        employment_type,
        company_size,
        remote_preference,
        excluded_condition_type,
        portfolio_link_type,
    ]:
        enum_type.create(bind, checkfirst=True)

    op.create_table(
        "career_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("headline", sa.String(length=160), nullable=True),
        sa.Column("career_level", career_level, nullable=False),
        sa.Column("years_of_experience", sa.Integer(), server_default="0", nullable=False),
        sa.Column("desired_job_title", sa.String(length=100), nullable=False),
        sa.Column("introduction", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_career_profiles_user_id", "career_profiles", ["user_id"])

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("normalized_name", sa.String(length=80), nullable=False),
        sa.Column("category", skill_category, server_default="ETC", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_skills_normalized_name", "skills", ["normalized_name"], unique=True)

    op.create_table(
        "user_skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("proficiency_level", proficiency_level, nullable=False),
        sa.Column("years_of_experience", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "skill_id", name="uq_user_skills_user_skill"),
    )
    op.create_index("ix_user_skills_user_id", "user_skills", ["user_id"])
    op.create_index("ix_user_skills_skill_id", "user_skills", ["skill_id"])

    op.create_table(
        "experiences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("company_name", sa.String(length=120), nullable=False),
        sa.Column("position", sa.String(length=120), nullable=False),
        sa.Column("employment_type", employment_type, nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_current", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("achievements", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_experiences_user_id", "experiences", ["user_id"])

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("summary", sa.String(length=300), nullable=True),
        sa.Column("role", sa.String(length=120), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_ongoing", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("responsibilities", sa.Text(), nullable=True),
        sa.Column("achievements", sa.Text(), nullable=True),
        sa.Column("repository_url", sa.String(length=500), nullable=True),
        sa.Column("service_url", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_projects_user_id", "projects", ["user_id"])

    op.create_table(
        "project_skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "skill_id", name="uq_project_skills_project_skill"),
    )
    op.create_index("ix_project_skills_project_id", "project_skills", ["project_id"])
    op.create_index("ix_project_skills_skill_id", "project_skills", ["skill_id"])

    op.create_table(
        "job_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("preferred_employment_types", sa.JSON(), nullable=False),
        sa.Column("preferred_locations", sa.JSON(), nullable=False),
        sa.Column("preferred_company_sizes", sa.JSON(), nullable=False),
        sa.Column("remote_preference", remote_preference, server_default="ANY", nullable=False),
        sa.Column("minimum_salary", sa.Integer(), nullable=True),
        sa.Column("desired_roles", sa.JSON(), nullable=False),
        sa.Column("priority_keywords", sa.JSON(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_job_preferences_user_id", "job_preferences", ["user_id"])

    op.create_table(
        "excluded_conditions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("condition_type", excluded_condition_type, nullable=False),
        sa.Column("value", sa.String(length=160), nullable=False),
        sa.Column("reason", sa.String(length=300), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "condition_type", "value", name="uq_excluded_conditions_user_type_value"
        ),
    )
    op.create_index("ix_excluded_conditions_user_id", "excluded_conditions", ["user_id"])
    op.create_index(
        "ix_excluded_conditions_user_active", "excluded_conditions", ["user_id", "is_active"]
    )

    op.create_table(
        "portfolio_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("link_type", portfolio_link_type, nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("display_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "url", name="uq_portfolio_links_user_url"),
    )
    op.create_index("ix_portfolio_links_user_id", "portfolio_links", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_portfolio_links_user_id", table_name="portfolio_links")
    op.drop_table("portfolio_links")
    op.drop_index("ix_excluded_conditions_user_active", table_name="excluded_conditions")
    op.drop_index("ix_excluded_conditions_user_id", table_name="excluded_conditions")
    op.drop_table("excluded_conditions")
    op.drop_index("ix_job_preferences_user_id", table_name="job_preferences")
    op.drop_table("job_preferences")
    op.drop_index("ix_project_skills_skill_id", table_name="project_skills")
    op.drop_index("ix_project_skills_project_id", table_name="project_skills")
    op.drop_table("project_skills")
    op.drop_index("ix_projects_user_id", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_experiences_user_id", table_name="experiences")
    op.drop_table("experiences")
    op.drop_index("ix_user_skills_skill_id", table_name="user_skills")
    op.drop_index("ix_user_skills_user_id", table_name="user_skills")
    op.drop_table("user_skills")
    op.drop_index("ix_skills_normalized_name", table_name="skills")
    op.drop_table("skills")
    op.drop_index("ix_career_profiles_user_id", table_name="career_profiles")
    op.drop_table("career_profiles")

    bind = op.get_bind()
    for enum_type in [
        portfolio_link_type,
        excluded_condition_type,
        remote_preference,
        company_size,
        employment_type,
        proficiency_level,
        skill_category,
        career_level,
    ]:
        enum_type.drop(bind, checkfirst=True)
