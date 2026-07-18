import enum
from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CareerLevel(str, enum.Enum):
    ENTRY = "ENTRY"
    JUNIOR = "JUNIOR"
    MID = "MID"
    SENIOR = "SENIOR"
    CAREER_CHANGE = "CAREER_CHANGE"


class SkillCategory(str, enum.Enum):
    LANGUAGE = "LANGUAGE"
    FRAMEWORK = "FRAMEWORK"
    DATABASE = "DATABASE"
    AI_ML = "AI_ML"
    DEVOPS = "DEVOPS"
    CLOUD = "CLOUD"
    FRONTEND = "FRONTEND"
    BACKEND = "BACKEND"
    TOOL = "TOOL"
    ETC = "ETC"


class ProficiencyLevel(str, enum.Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class EmploymentType(str, enum.Enum):
    FULL_TIME = "FULL_TIME"
    CONTRACT = "CONTRACT"
    INTERN = "INTERN"
    FREELANCE = "FREELANCE"
    PART_TIME = "PART_TIME"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    OTHER = "OTHER"


class CompanySize(str, enum.Enum):
    LARGE_ENTERPRISE = "LARGE_ENTERPRISE"
    MAJOR_AFFILIATE = "MAJOR_AFFILIATE"
    MID_SIZED = "MID_SIZED"
    SMALL_BUSINESS = "SMALL_BUSINESS"
    STARTUP = "STARTUP"
    PUBLIC_ORGANIZATION = "PUBLIC_ORGANIZATION"
    ANY = "ANY"


class RemotePreference(str, enum.Enum):
    ONSITE = "ONSITE"
    HYBRID = "HYBRID"
    REMOTE = "REMOTE"
    ANY = "ANY"


class ExcludedConditionType(str, enum.Enum):
    EMPLOYMENT_TYPE = "EMPLOYMENT_TYPE"
    LOCATION = "LOCATION"
    COMPANY_SIZE = "COMPANY_SIZE"
    REQUIRED_SKILL = "REQUIRED_SKILL"
    EXCLUDED_KEYWORD = "EXCLUDED_KEYWORD"
    MINIMUM_EXPERIENCE = "MINIMUM_EXPERIENCE"
    EDUCATION_REQUIREMENT = "EDUCATION_REQUIREMENT"
    OTHER = "OTHER"


class PortfolioLinkType(str, enum.Enum):
    GITHUB = "GITHUB"
    NOTION = "NOTION"
    PORTFOLIO = "PORTFOLIO"
    BLOG = "BLOG"
    LINKEDIN = "LINKEDIN"
    OTHER = "OTHER"


class CareerProfile(Base):
    __tablename__ = "career_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    headline: Mapped[str | None] = mapped_column(String(160), nullable=True)
    career_level: Mapped[CareerLevel] = mapped_column(
        Enum(CareerLevel, name="career_level"), nullable=False
    )
    years_of_experience: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    desired_job_title: Mapped[str] = mapped_column(String(100), nullable=False)
    introduction: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    normalized_name: Mapped[str] = mapped_column(
        String(80), nullable=False, unique=True, index=True
    )
    category: Mapped[SkillCategory] = mapped_column(
        Enum(SkillCategory, name="skill_category"),
        nullable=False,
        default=SkillCategory.ETC,
        server_default=SkillCategory.ETC.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class UserSkill(Base):
    __tablename__ = "user_skills"
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_user_skills_user_skill"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    proficiency_level: Mapped[ProficiencyLevel] = mapped_column(
        Enum(ProficiencyLevel, name="proficiency_level"), nullable=False
    )
    years_of_experience: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    skill: Mapped[Skill] = relationship("Skill")


class Experience(Base):
    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    company_name: Mapped[str] = mapped_column(String(120), nullable=False)
    position: Mapped[str] = mapped_column(String(120), nullable=False)
    employment_type: Mapped[EmploymentType] = mapped_column(
        Enum(EmploymentType, name="employment_type"), nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    achievements: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    summary: Mapped[str | None] = mapped_column(String(300), nullable=True)
    role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_ongoing: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsibilities: Mapped[str | None] = mapped_column(Text, nullable=True)
    achievements: Mapped[str | None] = mapped_column(Text, nullable=True)
    repository_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    service_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    project_skills: Mapped[list["ProjectSkill"]] = relationship(
        "ProjectSkill", cascade="all, delete-orphan"
    )


class ProjectSkill(Base):
    __tablename__ = "project_skills"
    __table_args__ = (
        UniqueConstraint("project_id", "skill_id", name="uq_project_skills_project_skill"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    skill: Mapped[Skill] = relationship("Skill")


class JobPreference(Base):
    __tablename__ = "job_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    preferred_employment_types: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    preferred_locations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    preferred_company_sizes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    remote_preference: Mapped[RemotePreference] = mapped_column(
        Enum(RemotePreference, name="remote_preference"),
        nullable=False,
        default=RemotePreference.ANY,
        server_default=RemotePreference.ANY.value,
    )
    minimum_salary: Mapped[int | None] = mapped_column(Integer, nullable=True)
    desired_roles: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    priority_keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class ExcludedCondition(Base):
    __tablename__ = "excluded_conditions"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "condition_type", "value", name="uq_excluded_conditions_user_type_value"
        ),
        Index("ix_excluded_conditions_user_active", "user_id", "is_active"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    condition_type: Mapped[ExcludedConditionType] = mapped_column(
        Enum(ExcludedConditionType, name="excluded_condition_type"), nullable=False
    )
    value: Mapped[str] = mapped_column(String(160), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(300), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class PortfolioLink(Base):
    __tablename__ = "portfolio_links"
    __table_args__ = (UniqueConstraint("user_id", "url", name="uq_portfolio_links_user_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    link_type: Mapped[PortfolioLinkType] = mapped_column(
        Enum(PortfolioLinkType, name="portfolio_link_type"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_primary: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    display_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
