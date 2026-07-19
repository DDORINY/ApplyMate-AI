import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ApplicationDocumentType(str, enum.Enum):
    MOTIVATION = "MOTIVATION"
    JOB_COMPETENCY = "JOB_COMPETENCY"
    SELF_INTRODUCTION = "SELF_INTRODUCTION"
    PROJECT_EXPERIENCE = "PROJECT_EXPERIENCE"
    CAREER_EXPERIENCE = "CAREER_EXPERIENCE"
    FUTURE_PLAN = "FUTURE_PLAN"
    FREE_FORM = "FREE_FORM"
    CUSTOM_QUESTION = "CUSTOM_QUESTION"


class ApplicationDocumentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    ARCHIVED = "ARCHIVED"


class ApplicationDocumentTone(str, enum.Enum):
    PROFESSIONAL = "PROFESSIONAL"
    CONCISE = "CONCISE"
    CONFIDENT = "CONFIDENT"
    HUMBLE = "HUMBLE"
    TECHNICAL = "TECHNICAL"
    STORYTELLING = "STORYTELLING"


class GenerationRunStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    INVALID_OUTPUT = "INVALID_OUTPUT"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"


class ApplicationDocument(Base):
    __tablename__ = "application_documents"
    __table_args__ = (
        Index("ix_application_documents_user_id", "user_id"),
        Index("ix_application_documents_user_status", "user_id", "status"),
        Index("ix_application_documents_user_type", "user_id", "document_type"),
        Index("ix_application_documents_user_archived", "user_id", "is_archived"),
        Index("ix_application_documents_job_id", "job_id"),
        Index("ix_application_documents_resume_id", "resume_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("job_postings.id", ondelete="SET NULL"), nullable=True)
    resume_id: Mapped[int | None] = mapped_column(ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)
    resume_file_id: Mapped[int | None] = mapped_column(ForeignKey("resume_files.id", ondelete="SET NULL"), nullable=True)
    resume_analysis_id: Mapped[int | None] = mapped_column(ForeignKey("resume_analyses.id", ondelete="SET NULL"), nullable=True)
    job_analysis_id: Mapped[int | None] = mapped_column(ForeignKey("job_analyses.id", ondelete="SET NULL"), nullable=True)
    job_match_id: Mapped[int | None] = mapped_column(ForeignKey("job_matches.id", ondelete="SET NULL"), nullable=True)
    document_type: Mapped[ApplicationDocumentType] = mapped_column(
        Enum(ApplicationDocumentType, name="application_document_type"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    question: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    tone: Mapped[ApplicationDocumentTone] = mapped_column(
        Enum(ApplicationDocumentTone, name="application_document_tone"),
        nullable=False,
        default=ApplicationDocumentTone.PROFESSIONAL,
        server_default=ApplicationDocumentTone.PROFESSIONAL.value,
    )
    language: Mapped[str] = mapped_column(String(20), nullable=False, default="ko", server_default="ko")
    character_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    minimum_character_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_character_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    maximum_character_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    focus_points: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    avoid_phrases: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    settings: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[ApplicationDocumentStatus] = mapped_column(
        Enum(ApplicationDocumentStatus, name="application_document_status"),
        nullable=False,
        default=ApplicationDocumentStatus.DRAFT,
        server_default=ApplicationDocumentStatus.DRAFT.value,
    )
    current_version_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    versions = relationship("ApplicationDocumentVersion", back_populates="document", cascade="all, delete-orphan")
    sources = relationship("ApplicationDocumentSource", back_populates="document", cascade="all, delete-orphan")
    generation_runs = relationship("GenerationRun", back_populates="document", cascade="all, delete-orphan")


class ApplicationDocumentVersion(Base):
    __tablename__ = "application_document_versions"
    __table_args__ = (
        UniqueConstraint("document_id", "version_number", name="uq_application_document_versions_document_version"),
        Index("ix_application_document_versions_user_id", "user_id"),
        Index("ix_application_document_versions_document_id", "document_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("application_documents.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_blocks: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    character_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    character_count_without_spaces: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    paragraph_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    limit_exceeded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    is_user_edited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    generation_run_id: Mapped[int | None] = mapped_column(ForeignKey("generation_runs.id", ondelete="SET NULL"), nullable=True)
    change_summary: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    document = relationship("ApplicationDocument", back_populates="versions")


class ApplicationDocumentSource(Base):
    __tablename__ = "application_document_sources"
    __table_args__ = (
        Index("ix_application_document_sources_user_id", "user_id"),
        Index("ix_application_document_sources_document_id", "document_id"),
        Index("ix_application_document_sources_version_id", "version_id"),
        Index("ix_application_document_sources_source", "source_type", "source_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("application_documents.id", ondelete="CASCADE"), nullable=False)
    version_id: Mapped[int] = mapped_column(ForeignKey("application_document_versions.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[str] = mapped_column(String(80), nullable=False)
    source_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    field_path: Mapped[str | None] = mapped_column(String(300), nullable=True)
    source_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    evidence: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    document = relationship("ApplicationDocument", back_populates="sources")


class GenerationRun(Base):
    __tablename__ = "generation_runs"
    __table_args__ = (
        Index("ix_generation_runs_user_id", "user_id"),
        Index("ix_generation_runs_document_id", "document_id"),
        Index("ix_generation_runs_user_status", "user_id", "status"),
        Index("ix_generation_runs_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("application_documents.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[GenerationRunStatus] = mapped_column(
        Enum(GenerationRunStatus, name="generation_run_status"),
        nullable=False,
        default=GenerationRunStatus.PENDING,
        server_default=GenerationRunStatus.PENDING.value,
    )
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    prompt_version: Mapped[str] = mapped_column(String(30), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(30), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    settings: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    safe_error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    usage_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    result_snapshot: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    document = relationship("ApplicationDocument", back_populates="generation_runs")
