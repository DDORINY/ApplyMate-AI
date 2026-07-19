import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    JSON,
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


class JobAnalysisStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class JobMatchStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class JobMatchGrade(str, enum.Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    MODERATE = "MODERATE"
    LOW = "LOW"
    VERY_LOW = "VERY_LOW"


class JobMatchRecommendationStatus(str, enum.Enum):
    STRONGLY_RECOMMENDED = "STRONGLY_RECOMMENDED"
    RECOMMENDED = "RECOMMENDED"
    CONSIDER = "CONSIDER"
    NOT_RECOMMENDED = "NOT_RECOMMENDED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class JobMatchFeedbackType(str, enum.Enum):
    ACCURATE = "ACCURATE"
    TOO_HIGH = "TOO_HIGH"
    TOO_LOW = "TOO_LOW"
    MISSING_STRENGTH = "MISSING_STRENGTH"
    MISSING_RISK = "MISSING_RISK"
    OTHER = "OTHER"


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
    analysis = relationship(
        "JobAnalysis", back_populates="job_posting", cascade="all, delete-orphan", uselist=False
    )
    analysis_runs = relationship(
        "JobAnalysisRun", back_populates="job_posting", cascade="all, delete-orphan"
    )
    match = relationship(
        "JobMatch", back_populates="job_posting", cascade="all, delete-orphan", uselist=False
    )


class JobAnalysis(Base):
    __tablename__ = "job_analyses"
    __table_args__ = (
        Index("ix_job_analyses_user_id", "user_id"),
        Index("ix_job_analyses_user_status", "user_id", "status"),
        UniqueConstraint("job_posting_id", name="uq_job_analyses_job_posting_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_posting_id: Mapped[int] = mapped_column(
        ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[JobAnalysisStatus] = mapped_column(
        Enum(JobAnalysisStatus, name="job_analysis_status"),
        nullable=False,
        default=JobAnalysisStatus.PENDING,
        server_default=JobAnalysisStatus.PENDING.value,
    )
    schema_version: Mapped[str] = mapped_column(String(30), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(30), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    input_length: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    position_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    responsibilities: Mapped[list | None] = mapped_column(JSON, nullable=True)
    required_qualifications: Mapped[list | None] = mapped_column(JSON, nullable=True)
    preferred_qualifications: Mapped[list | None] = mapped_column(JSON, nullable=True)
    technical_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    experience_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    education_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    work_conditions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    recruitment_process: Mapped[list | None] = mapped_column(JSON, nullable=True)
    deadline_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    company_values: Mapped[list | None] = mapped_column(JSON, nullable=True)
    keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    warnings: Mapped[list | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_user_edited: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    job_posting = relationship("JobPosting", back_populates="analysis")
    runs = relationship("JobAnalysisRun", back_populates="analysis")


class JobAnalysisRun(Base):
    __tablename__ = "job_analysis_runs"
    __table_args__ = (
        Index("ix_job_analysis_runs_user_id", "user_id"),
        Index("ix_job_analysis_runs_job_posting_id", "job_posting_id"),
        Index("ix_job_analysis_runs_user_status", "user_id", "status"),
        Index("ix_job_analysis_runs_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_posting_id: Mapped[int] = mapped_column(
        ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False
    )
    job_analysis_id: Mapped[int | None] = mapped_column(
        ForeignKey("job_analyses.id", ondelete="SET NULL"), nullable=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[JobAnalysisStatus] = mapped_column(
        Enum(JobAnalysisStatus, name="job_analysis_status"),
        nullable=False,
        default=JobAnalysisStatus.PROCESSING,
        server_default=JobAnalysisStatus.PROCESSING.value,
    )
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    schema_version: Mapped[str] = mapped_column(String(30), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(30), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    input_length: Mapped[int] = mapped_column(Integer, nullable=False)
    request_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    job_posting = relationship("JobPosting", back_populates="analysis_runs")
    analysis = relationship("JobAnalysis", back_populates="runs")


class JobMatch(Base):
    __tablename__ = "job_matches"
    __table_args__ = (
        Index("ix_job_matches_user_id", "user_id"),
        Index("ix_job_matches_user_grade", "user_id", "grade"),
        Index("ix_job_matches_user_recommendation", "user_id", "recommendation_status"),
        UniqueConstraint("user_id", "job_posting_id", name="uq_job_matches_user_job"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_posting_id: Mapped[int] = mapped_column(
        ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False
    )
    job_analysis_id: Mapped[int] = mapped_column(
        ForeignKey("job_analyses.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[JobMatchStatus] = mapped_column(
        Enum(JobMatchStatus, name="job_match_status"),
        nullable=False,
        default=JobMatchStatus.PENDING,
        server_default=JobMatchStatus.PENDING.value,
    )
    total_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    grade: Mapped[JobMatchGrade] = mapped_column(
        Enum(JobMatchGrade, name="job_match_grade"),
        nullable=False,
        default=JobMatchGrade.VERY_LOW,
        server_default=JobMatchGrade.VERY_LOW.value,
    )
    recommendation_status: Mapped[JobMatchRecommendationStatus] = mapped_column(
        Enum(JobMatchRecommendationStatus, name="job_match_recommendation_status"),
        nullable=False,
        default=JobMatchRecommendationStatus.INSUFFICIENT_DATA,
        server_default=JobMatchRecommendationStatus.INSUFFICIENT_DATA.value,
    )
    role_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    skill_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    experience_score: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    project_score: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    preference_score: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    matched_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    missing_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    matched_projects: Mapped[list | None] = mapped_column(JSON, nullable=True)
    strengths: Mapped[list | None] = mapped_column(JSON, nullable=True)
    gaps: Mapped[list | None] = mapped_column(JSON, nullable=True)
    risks: Mapped[list | None] = mapped_column(JSON, nullable=True)
    recommendation_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_completeness: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    profile_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    job_analysis_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    calculation_version: Mapped[str] = mapped_column(String(30), nullable=False)
    explanation_provider: Mapped[str] = mapped_column(String(30), nullable=False)
    calculated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    job_posting = relationship("JobPosting", back_populates="match")
    job_analysis = relationship("JobAnalysis")
    runs = relationship("JobMatchRun", back_populates="match")
    feedback = relationship("JobMatchFeedback", back_populates="match", cascade="all, delete-orphan")


class JobMatchRun(Base):
    __tablename__ = "job_match_runs"
    __table_args__ = (
        Index("ix_job_match_runs_user_id", "user_id"),
        Index("ix_job_match_runs_job_posting_id", "job_posting_id"),
        Index("ix_job_match_runs_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_match_id: Mapped[int | None] = mapped_column(
        ForeignKey("job_matches.id", ondelete="SET NULL"), nullable=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_posting_id: Mapped[int] = mapped_column(
        ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False
    )
    job_analysis_id: Mapped[int] = mapped_column(
        ForeignKey("job_analyses.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[JobMatchStatus] = mapped_column(
        Enum(JobMatchStatus, name="job_match_status"),
        nullable=False,
        default=JobMatchStatus.PROCESSING,
        server_default=JobMatchStatus.PROCESSING.value,
    )
    profile_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    job_analysis_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    calculation_version: Mapped[str] = mapped_column(String(30), nullable=False)
    total_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    result_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    match = relationship("JobMatch", back_populates="runs")


class JobMatchFeedback(Base):
    __tablename__ = "job_match_feedback"
    __table_args__ = (Index("ix_job_match_feedback_user_match", "user_id", "job_match_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_match_id: Mapped[int] = mapped_column(
        ForeignKey("job_matches.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    feedback_type: Mapped[JobMatchFeedbackType] = mapped_column(
        Enum(JobMatchFeedbackType, name="job_match_feedback_type"), nullable=False
    )
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    match = relationship("JobMatch", back_populates="feedback")
