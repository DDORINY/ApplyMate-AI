import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
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


class CompanySize(str, enum.Enum):
    LARGE_ENTERPRISE = "LARGE_ENTERPRISE"
    MAJOR_AFFILIATE = "MAJOR_AFFILIATE"
    MID_SIZED = "MID_SIZED"
    SMALL_BUSINESS = "SMALL_BUSINESS"
    STARTUP = "STARTUP"
    PUBLIC_ORGANIZATION = "PUBLIC_ORGANIZATION"
    UNKNOWN = "UNKNOWN"


class JobSourceType(str, enum.Enum):
    MANUAL = "MANUAL"
    URL = "URL"


class JobPostingStatus(str, enum.Enum):
    SAVED = "SAVED"
    REVIEWING = "REVIEWING"
    INTERESTED = "INTERESTED"
    EXCLUDED = "EXCLUDED"
    CLOSED = "CLOSED"


class JobEmploymentType(str, enum.Enum):
    FULL_TIME = "FULL_TIME"
    CONTRACT = "CONTRACT"
    INTERN = "INTERN"
    PART_TIME = "PART_TIME"
    FREELANCE = "FREELANCE"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class JobWorkType(str, enum.Enum):
    ONSITE = "ONSITE"
    HYBRID = "HYBRID"
    REMOTE = "REMOTE"
    UNKNOWN = "UNKNOWN"


class JobDeadlineType(str, enum.Enum):
    FIXED = "FIXED"
    UNTIL_FILLED = "UNTIL_FILLED"
    ONGOING = "ONGOING"
    UNKNOWN = "UNKNOWN"


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (Index("ix_companies_normalized_name", "normalized_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    company_size: Mapped[CompanySize] = mapped_column(
        Enum(CompanySize, name="company_size_v2"),
        nullable=False,
        default=CompanySize.UNKNOWN,
        server_default=CompanySize.UNKNOWN.value,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    job_postings = relationship("JobPosting", back_populates="company")


class JobPosting(Base):
    __tablename__ = "job_postings"
    __table_args__ = (
        Index("ix_job_postings_user_id", "user_id"),
        Index("ix_job_postings_company_id", "company_id"),
        Index("ix_job_postings_user_status", "user_id", "status"),
        Index("ix_job_postings_user_deadline", "user_id", "deadline_at"),
        Index("ix_job_postings_user_favorite", "user_id", "is_favorite"),
        Index("ix_job_postings_user_source_type", "user_id", "source_type"),
        UniqueConstraint("user_id", "source_url", name="uq_job_postings_user_source_url"),
        UniqueConstraint("user_id", "content_hash", name="uq_job_postings_user_content_hash"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[str | None] = mapped_column(String(160), nullable=True)
    employment_type: Mapped[JobEmploymentType] = mapped_column(
        Enum(JobEmploymentType, name="job_employment_type"),
        nullable=False,
        default=JobEmploymentType.UNKNOWN,
        server_default=JobEmploymentType.UNKNOWN.value,
    )
    career_requirement: Mapped[str | None] = mapped_column(String(300), nullable=True)
    education_requirement: Mapped[str | None] = mapped_column(String(300), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    work_type: Mapped[JobWorkType] = mapped_column(
        Enum(JobWorkType, name="job_work_type"),
        nullable=False,
        default=JobWorkType.UNKNOWN,
        server_default=JobWorkType.UNKNOWN.value,
    )
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_text: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_qualifications: Mapped[str | None] = mapped_column(Text, nullable=True)
    benefits: Mapped[str | None] = mapped_column(Text, nullable=True)
    recruitment_process: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[JobSourceType] = mapped_column(
        Enum(JobSourceType, name="job_source_type"),
        nullable=False,
        default=JobSourceType.MANUAL,
        server_default=JobSourceType.MANUAL.value,
    )
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    source_site: Mapped[str | None] = mapped_column(String(120), nullable=True)
    original_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deadline_type: Mapped[JobDeadlineType] = mapped_column(
        Enum(JobDeadlineType, name="job_deadline_type"),
        nullable=False,
        default=JobDeadlineType.UNKNOWN,
        server_default=JobDeadlineType.UNKNOWN.value,
    )
    status: Mapped[JobPostingStatus] = mapped_column(
        Enum(JobPostingStatus, name="job_posting_status"),
        nullable=False,
        default=JobPostingStatus.SAVED,
        server_default=JobPostingStatus.SAVED.value,
    )
    is_favorite: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company", back_populates="job_postings")
