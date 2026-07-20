import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DocumentImprovementType(str, enum.Enum):
    CLARITY = "CLARITY"
    CONCISENESS = "CONCISENESS"
    PROFESSIONAL_TONE = "PROFESSIONAL_TONE"
    JOB_ALIGNMENT = "JOB_ALIGNMENT"
    COMPANY_ALIGNMENT = "COMPANY_ALIGNMENT"
    SKILL_EMPHASIS = "SKILL_EMPHASIS"
    EXPERIENCE_EMPHASIS = "EXPERIENCE_EMPHASIS"
    PROJECT_EMPHASIS = "PROJECT_EMPHASIS"
    ACHIEVEMENT_EMPHASIS = "ACHIEVEMENT_EMPHASIS"
    STRUCTURE = "STRUCTURE"
    GRAMMAR = "GRAMMAR"
    LENGTH_REDUCTION = "LENGTH_REDUCTION"
    LENGTH_EXPANSION = "LENGTH_EXPANSION"
    CUSTOM = "CUSTOM"


class DocumentImprovementRunStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    INVALID_OUTPUT = "INVALID_OUTPUT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"


class DocumentImprovementSuggestionStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"


class DocumentImprovementChangeType(str, enum.Enum):
    REWRITE = "REWRITE"
    ADD = "ADD"
    DELETE = "DELETE"
    STRUCTURE = "STRUCTURE"
    GRAMMAR = "GRAMMAR"
    TONE = "TONE"
    LENGTH = "LENGTH"


class DocumentImprovementRiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DocumentImprovementSourceType(str, enum.Enum):
    PROFILE = "PROFILE"
    RESUME_TEXT = "RESUME_TEXT"
    RESUME_ANALYSIS = "RESUME_ANALYSIS"
    JOB_POSTING = "JOB_POSTING"
    JOB_ANALYSIS = "JOB_ANALYSIS"
    MATCH_ANALYSIS = "MATCH_ANALYSIS"
    CURRENT_DOCUMENT = "CURRENT_DOCUMENT"
    USER_INSTRUCTION = "USER_INSTRUCTION"


class DocumentImprovementActionType(str, enum.Enum):
    SUGGESTION_APPROVED = "SUGGESTION_APPROVED"
    SUGGESTION_REJECTED = "SUGGESTION_REJECTED"
    RUN_APPLIED = "RUN_APPLIED"
    RUN_REJECTED = "RUN_REJECTED"
    RUN_DELETED = "RUN_DELETED"


class DocumentImprovementRun(Base):
    __tablename__ = "document_improvement_runs"
    __table_args__ = (
        Index("ix_document_improvement_runs_user_document", "user_id", "application_document_id"),
        Index("ix_document_improvement_runs_user_status", "user_id", "status"),
        Index("ix_document_improvement_runs_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    application_document_id: Mapped[int] = mapped_column(ForeignKey("application_documents.id", ondelete="CASCADE"), nullable=False)
    base_version_id: Mapped[int] = mapped_column(ForeignKey("application_document_versions.id", ondelete="CASCADE"), nullable=False)
    result_version_id: Mapped[int | None] = mapped_column(ForeignKey("application_document_versions.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[DocumentImprovementRunStatus] = mapped_column(
        Enum(DocumentImprovementRunStatus, name="document_improvement_run_status"),
        nullable=False,
        default=DocumentImprovementRunStatus.PENDING,
        server_default=DocumentImprovementRunStatus.PENDING.value,
    )
    improvement_type: Mapped[DocumentImprovementType] = mapped_column(
        Enum(DocumentImprovementType, name="document_improvement_type"), nullable=False
    )
    custom_instruction: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_min_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_max_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_tone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    prompt_version: Mapped[str] = mapped_column(String(30), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(30), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    source_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    outdated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    safe_error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    overall_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    suggested_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    warnings: Mapped[list | None] = mapped_column(JSON, nullable=True)
    missing_information: Mapped[list | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    usage_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    suggestions = relationship("DocumentImprovementSuggestion", back_populates="run", cascade="all, delete-orphan")
    sources = relationship("DocumentImprovementSource", back_populates="run", cascade="all, delete-orphan")
    actions = relationship("DocumentImprovementAction", back_populates="run", cascade="all, delete-orphan")


class DocumentImprovementSuggestion(Base):
    __tablename__ = "document_improvement_suggestions"
    __table_args__ = (
        Index("ix_document_improvement_suggestions_run", "run_id"),
        Index("ix_document_improvement_suggestions_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("document_improvement_runs.id", ondelete="CASCADE"), nullable=False)
    paragraph_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    sentence_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_text: Mapped[str] = mapped_column(Text, nullable=False)
    change_type: Mapped[DocumentImprovementChangeType] = mapped_column(
        Enum(DocumentImprovementChangeType, name="document_improvement_change_type"), nullable=False
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    risk_level: Mapped[DocumentImprovementRiskLevel] = mapped_column(
        Enum(DocumentImprovementRiskLevel, name="document_improvement_risk_level"),
        nullable=False,
        default=DocumentImprovementRiskLevel.LOW,
        server_default=DocumentImprovementRiskLevel.LOW.value,
    )
    status: Mapped[DocumentImprovementSuggestionStatus] = mapped_column(
        Enum(DocumentImprovementSuggestionStatus, name="document_improvement_suggestion_status"),
        nullable=False,
        default=DocumentImprovementSuggestionStatus.PENDING,
        server_default=DocumentImprovementSuggestionStatus.PENDING.value,
    )
    selected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    run = relationship("DocumentImprovementRun", back_populates="suggestions")


class DocumentImprovementSource(Base):
    __tablename__ = "document_improvement_sources"
    __table_args__ = (
        Index("ix_document_improvement_sources_run", "run_id"),
        Index("ix_document_improvement_sources_source", "source_type", "source_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("document_improvement_runs.id", ondelete="CASCADE"), nullable=False)
    source_type: Mapped[DocumentImprovementSourceType] = mapped_column(
        Enum(DocumentImprovementSourceType, name="document_improvement_source_type"), nullable=False
    )
    source_id: Mapped[str] = mapped_column(String(80), nullable=False)
    source_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    source_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    run = relationship("DocumentImprovementRun", back_populates="sources")


class DocumentImprovementAction(Base):
    __tablename__ = "document_improvement_actions"
    __table_args__ = (
        Index("ix_document_improvement_actions_user_run", "user_id", "run_id"),
        Index("ix_document_improvement_actions_suggestion", "suggestion_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    run_id: Mapped[int] = mapped_column(ForeignKey("document_improvement_runs.id", ondelete="CASCADE"), nullable=False)
    suggestion_id: Mapped[int | None] = mapped_column(ForeignKey("document_improvement_suggestions.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[DocumentImprovementActionType] = mapped_column(
        Enum(DocumentImprovementActionType, name="document_improvement_action_type"), nullable=False
    )
    previous_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    run = relationship("DocumentImprovementRun", back_populates="actions")
