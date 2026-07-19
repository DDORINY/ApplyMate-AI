import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.integration import ExternalProvider


class GmailConnectionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    REAUTH_REQUIRED = "REAUTH_REQUIRED"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"


class EmailSyncRunStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL_FAILED = "PARTIAL_FAILED"


class EmailProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    IGNORED = "IGNORED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class EmailCandidateType(str, enum.Enum):
    APPLICATION_RECEIVED = "APPLICATION_RECEIVED"
    DOCUMENT_REVIEW = "DOCUMENT_REVIEW"
    CODING_TEST = "CODING_TEST"
    ASSIGNMENT = "ASSIGNMENT"
    INTERVIEW = "INTERVIEW"
    FINAL_INTERVIEW = "FINAL_INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    SCHEDULE_CHANGE = "SCHEDULE_CHANGE"
    RECRUITER_CONTACT = "RECRUITER_CONTACT"
    OTHER = "OTHER"


class EmailCandidateStatus(str, enum.Enum):
    NEW = "NEW"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"
    EXPIRED = "EXPIRED"


class EmailCandidateActionType(str, enum.Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    LINKED_APPLICATION = "LINKED_APPLICATION"
    STATUS_CHANGED = "STATUS_CHANGED"
    SCHEDULE_CREATED = "SCHEDULE_CREATED"


class GmailOAuthState(Base):
    __tablename__ = "gmail_oauth_states"
    __table_args__ = (
        Index("ix_gmail_oauth_states_state_hash", "state_hash"),
        Index("ix_gmail_oauth_states_expires_at", "expires_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[ExternalProvider] = mapped_column(Enum(ExternalProvider, name="external_provider"), nullable=False)
    state_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    redirect_path: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class GmailConnection(Base):
    __tablename__ = "gmail_connections"
    __table_args__ = (
        Index("ix_gmail_connections_user_id", "user_id"),
        Index("ix_gmail_connections_external_account_id", "external_account_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    external_account_id: Mapped[int] = mapped_column(ForeignKey("external_accounts.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[ExternalProvider] = mapped_column(Enum(ExternalProvider, name="external_provider"), nullable=False)
    status: Mapped[GmailConnectionStatus] = mapped_column(
        Enum(GmailConnectionStatus, name="gmail_connection_status"),
        nullable=False,
        default=GmailConnectionStatus.ACTIVE,
        server_default=GmailConnectionStatus.ACTIVE.value,
    )
    sync_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    search_query: Mapped[str] = mapped_column(Text, nullable=False)
    lookback_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30, server_default="30")
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    history_id_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    connected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    disconnected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    external_account = relationship("ExternalAccount", back_populates="gmail_connections")
    messages = relationship("EmailMessage", back_populates="connection")
    sync_runs = relationship("EmailSyncRun", back_populates="connection")


class EmailSyncRun(Base):
    __tablename__ = "email_sync_runs"
    __table_args__ = (Index("ix_email_sync_runs_user_connection", "user_id", "connection_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    connection_id: Mapped[int] = mapped_column(ForeignKey("gmail_connections.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[EmailSyncRunStatus] = mapped_column(Enum(EmailSyncRunStatus, name="email_sync_run_status"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scanned_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    matched_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    candidate_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    ignored_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    history_id_before: Mapped[str | None] = mapped_column(Text, nullable=True)
    history_id_after: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    connection = relationship("GmailConnection", back_populates="sync_runs")


class EmailMessage(Base):
    __tablename__ = "email_messages"
    __table_args__ = (
        UniqueConstraint("connection_id", "provider_message_id", name="uq_email_message_connection_provider"),
        Index("ix_email_messages_user_received", "user_id", "received_at"),
        Index("ix_email_messages_user_status", "user_id", "processing_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    connection_id: Mapped[int] = mapped_column(ForeignKey("gmail_connections.id", ondelete="CASCADE"), nullable=False)
    provider_message_id: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_thread_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sender: Mapped[str] = mapped_column(String(500), nullable=False)
    sender_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_text_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    sanitized_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_status: Mapped[EmailProcessingStatus] = mapped_column(
        Enum(EmailProcessingStatus, name="email_processing_status"),
        nullable=False,
        default=EmailProcessingStatus.PENDING,
        server_default=EmailProcessingStatus.PENDING.value,
    )
    classification: Mapped[str | None] = mapped_column(String(80), nullable=True)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    connection = relationship("GmailConnection", back_populates="messages")
    analysis_runs = relationship("EmailAnalysisRun", back_populates="email_message")
    candidates = relationship("EmailCandidate", back_populates="email_message")


class EmailAnalysisRun(Base):
    __tablename__ = "email_analysis_runs"
    __table_args__ = (Index("ix_email_analysis_runs_user_message", "user_id", "email_message_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    email_message_id: Mapped[int] = mapped_column(ForeignKey("email_messages.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[EmailProcessingStatus] = mapped_column(Enum(EmailProcessingStatus, name="email_processing_status"), nullable=False)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    prompt_version: Mapped[str] = mapped_column(String(40), nullable=False, default="v1", server_default="v1")
    schema_version: Mapped[str] = mapped_column(String(40), nullable=False, default="v1", server_default="v1")
    input_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    safe_error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    result_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    email_message = relationship("EmailMessage", back_populates="analysis_runs")
    candidates = relationship("EmailCandidate", back_populates="analysis_run")


class EmailCandidate(Base):
    __tablename__ = "email_candidates"
    __table_args__ = (
        Index("ix_email_candidates_user_status", "user_id", "status"),
        Index("ix_email_candidates_user_type", "user_id", "candidate_type"),
        Index("ix_email_candidates_application_id", "application_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    email_message_id: Mapped[int] = mapped_column(ForeignKey("email_messages.id", ondelete="CASCADE"), nullable=False)
    analysis_run_id: Mapped[int | None] = mapped_column(ForeignKey("email_analysis_runs.id", ondelete="SET NULL"), nullable=True)
    candidate_type: Mapped[EmailCandidateType] = mapped_column(Enum(EmailCandidateType, name="email_candidate_type"), nullable=False)
    status: Mapped[EmailCandidateStatus] = mapped_column(
        Enum(EmailCandidateStatus, name="email_candidate_status"),
        nullable=False,
        default=EmailCandidateStatus.NEW,
        server_default=EmailCandidateStatus.NEW.value,
    )
    company_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    application_id: Mapped[int | None] = mapped_column(ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)
    event_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    evidence: Mapped[dict] = mapped_column(JSON, nullable=False)
    requires_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    review_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    email_message = relationship("EmailMessage", back_populates="candidates")
    analysis_run = relationship("EmailAnalysisRun", back_populates="candidates")
    application = relationship("Application")
    actions = relationship("EmailCandidateAction", back_populates="candidate")


class EmailCandidateAction(Base):
    __tablename__ = "email_candidate_actions"
    __table_args__ = (Index("ix_email_candidate_actions_user_candidate", "user_id", "candidate_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("email_candidates.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[EmailCandidateActionType] = mapped_column(Enum(EmailCandidateActionType, name="email_candidate_action_type"), nullable=False)
    application_id: Mapped[int | None] = mapped_column(ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)
    schedule_event_id: Mapped[int | None] = mapped_column(ForeignKey("schedule_events.id", ondelete="SET NULL"), nullable=True)
    previous_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    candidate = relationship("EmailCandidate", back_populates="actions")
