import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
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


class JobRecommendationRunStatus(str, enum.Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class JobRecommendationGrade(str, enum.Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    POSSIBLE = "POSSIBLE"
    LOW = "LOW"
    BLOCKED = "BLOCKED"


class JobRecommendationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    OUTDATED = "OUTDATED"
    HIDDEN = "HIDDEN"
    ARCHIVED = "ARCHIVED"


class JobRecommendationType(str, enum.Enum):
    RULE_BASED = "RULE_BASED"


class JobRecommendationReasonType(str, enum.Enum):
    ROLE_MATCH = "ROLE_MATCH"
    SKILL_MATCH = "SKILL_MATCH"
    SKILL_MISSING = "SKILL_MISSING"
    EXPERIENCE_MATCH = "EXPERIENCE_MATCH"
    EXPERIENCE_GAP = "EXPERIENCE_GAP"
    EMPLOYMENT_TYPE_MATCH = "EMPLOYMENT_TYPE_MATCH"
    EMPLOYMENT_TYPE_MISMATCH = "EMPLOYMENT_TYPE_MISMATCH"
    LOCATION_MATCH = "LOCATION_MATCH"
    LOCATION_MISMATCH = "LOCATION_MISMATCH"
    PROJECT_MATCH = "PROJECT_MATCH"
    PREFERENCE_MATCH = "PREFERENCE_MATCH"
    DATA_INSUFFICIENT = "DATA_INSUFFICIENT"
    ALREADY_APPLIED = "ALREADY_APPLIED"
    USER_FEEDBACK_EXCLUDED = "USER_FEEDBACK_EXCLUDED"


class JobRecommendationRequirementType(str, enum.Enum):
    ROLE = "ROLE"
    SKILL = "SKILL"
    EXPERIENCE = "EXPERIENCE"
    EMPLOYMENT_TYPE = "EMPLOYMENT_TYPE"
    LOCATION = "LOCATION"
    PROJECT = "PROJECT"
    PREFERENCE = "PREFERENCE"
    DATA = "DATA"
    HISTORY = "HISTORY"


class JobRecommendationMatchStatus(str, enum.Enum):
    MATCHED = "MATCHED"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class JobRecommendationSeverity(str, enum.Enum):
    REQUIRED = "REQUIRED"
    PREFERRED = "PREFERRED"
    INFO = "INFO"


class JobRecommendationFeedbackType(str, enum.Enum):
    INTERESTED = "INTERESTED"
    NOT_INTERESTED = "NOT_INTERESTED"
    HIDDEN = "HIDDEN"
    APPLIED = "APPLIED"
    SAVED_FOR_LATER = "SAVED_FOR_LATER"


class JobRecommendationFeedbackReason(str, enum.Enum):
    LOCATION = "LOCATION"
    SALARY = "SALARY"
    ROLE = "ROLE"
    TECH_STACK = "TECH_STACK"
    EXPERIENCE = "EXPERIENCE"
    EMPLOYMENT_TYPE = "EMPLOYMENT_TYPE"
    COMPANY = "COMPANY"
    OTHER = "OTHER"


class JobRecommendationRun(Base):
    __tablename__ = "job_recommendation_runs"
    __table_args__ = (
        Index("ix_job_recommendation_runs_user_created", "user_id", "created_at"),
        Index("ix_job_recommendation_runs_user_status", "user_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[JobRecommendationRunStatus] = mapped_column(
        Enum(JobRecommendationRunStatus, name="job_recommendation_run_status"),
        nullable=False,
        default=JobRecommendationRunStatus.PROCESSING,
        server_default=JobRecommendationRunStatus.PROCESSING.value,
    )
    policy_version: Mapped[str] = mapped_column(String(40), nullable=False)
    input_job_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    recommended_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    excluded_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    safe_error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    recommendations = relationship("JobRecommendation", back_populates="run")


class JobRecommendation(Base):
    __tablename__ = "job_recommendations"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="ck_job_recommendations_score_range"),
        Index("ix_job_recommendations_user_score", "user_id", "score"),
        Index("ix_job_recommendations_user_grade", "user_id", "grade"),
        Index("ix_job_recommendations_user_status", "user_id", "status"),
        Index("ix_job_recommendations_user_generated", "user_id", "generated_at"),
        UniqueConstraint(
            "user_id",
            "job_id",
            "profile_hash",
            "job_hash",
            "policy_version",
            name="uq_job_recommendations_user_job_snapshot_policy",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False)
    run_id: Mapped[int] = mapped_column(ForeignKey("job_recommendation_runs.id", ondelete="CASCADE"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    grade: Mapped[JobRecommendationGrade] = mapped_column(
        Enum(JobRecommendationGrade, name="job_recommendation_grade"), nullable=False
    )
    recommendation_type: Mapped[JobRecommendationType] = mapped_column(
        Enum(JobRecommendationType, name="job_recommendation_type"),
        nullable=False,
        default=JobRecommendationType.RULE_BASED,
        server_default=JobRecommendationType.RULE_BASED.value,
    )
    has_blocking_mismatch: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    matched_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    missing_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    unknown_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    profile_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    job_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    resume_analysis_id: Mapped[int | None] = mapped_column(ForeignKey("resume_analyses.id", ondelete="SET NULL"), nullable=True)
    job_analysis_id: Mapped[int | None] = mapped_column(ForeignKey("job_analyses.id", ondelete="SET NULL"), nullable=True)
    matching_analysis_id: Mapped[int | None] = mapped_column(ForeignKey("job_matches.id", ondelete="SET NULL"), nullable=True)
    policy_version: Mapped[str] = mapped_column(String(40), nullable=False)
    input_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    score_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    missing_profile_fields: Mapped[list | None] = mapped_column(JSON, nullable=True)
    outdated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    status: Mapped[JobRecommendationStatus] = mapped_column(
        Enum(JobRecommendationStatus, name="job_recommendation_status"),
        nullable=False,
        default=JobRecommendationStatus.ACTIVE,
        server_default=JobRecommendationStatus.ACTIVE.value,
    )
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    job = relationship("JobPosting")
    run = relationship("JobRecommendationRun", back_populates="recommendations")
    reasons = relationship("JobRecommendationReason", back_populates="recommendation", cascade="all, delete-orphan")
    feedback = relationship("JobRecommendationFeedback", back_populates="recommendation", cascade="all, delete-orphan")


class JobRecommendationReason(Base):
    __tablename__ = "job_recommendation_reasons"
    __table_args__ = (
        Index("ix_job_recommendation_reasons_recommendation", "recommendation_id"),
        Index("ix_job_recommendation_reasons_type", "reason_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recommendation_id: Mapped[int] = mapped_column(ForeignKey("job_recommendations.id", ondelete="CASCADE"), nullable=False)
    reason_type: Mapped[JobRecommendationReasonType] = mapped_column(
        Enum(JobRecommendationReasonType, name="job_recommendation_reason_type"), nullable=False
    )
    requirement_type: Mapped[JobRecommendationRequirementType] = mapped_column(
        Enum(JobRecommendationRequirementType, name="job_recommendation_requirement_type"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    normalized_value: Mapped[str | None] = mapped_column(String(160), nullable=True)
    match_status: Mapped[JobRecommendationMatchStatus] = mapped_column(
        Enum(JobRecommendationMatchStatus, name="job_recommendation_match_status"), nullable=False
    )
    weight: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    score_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    severity: Mapped[JobRecommendationSeverity] = mapped_column(
        Enum(JobRecommendationSeverity, name="job_recommendation_severity"),
        nullable=False,
        default=JobRecommendationSeverity.INFO,
        server_default=JobRecommendationSeverity.INFO.value,
    )
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    recommendation = relationship("JobRecommendation", back_populates="reasons")


class JobRecommendationFeedback(Base):
    __tablename__ = "job_recommendation_feedback"
    __table_args__ = (
        Index("ix_job_recommendation_feedback_user_recommendation", "user_id", "recommendation_id"),
        UniqueConstraint("user_id", "recommendation_id", name="uq_job_recommendation_feedback_user_recommendation"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recommendation_id: Mapped[int] = mapped_column(ForeignKey("job_recommendations.id", ondelete="CASCADE"), nullable=False)
    feedback_type: Mapped[JobRecommendationFeedbackType] = mapped_column(
        Enum(JobRecommendationFeedbackType, name="job_recommendation_feedback_type"), nullable=False
    )
    reason_code: Mapped[JobRecommendationFeedbackReason | None] = mapped_column(
        Enum(JobRecommendationFeedbackReason, name="job_recommendation_feedback_reason"), nullable=True
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    recommendation = relationship("JobRecommendation", back_populates="feedback")
