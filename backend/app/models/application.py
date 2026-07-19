import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ApplicationStatus(str, enum.Enum):
    SAVED = "SAVED"
    PREPARING = "PREPARING"
    APPLIED = "APPLIED"
    DOCUMENT_REVIEW = "DOCUMENT_REVIEW"
    CODING_TEST = "CODING_TEST"
    ASSIGNMENT = "ASSIGNMENT"
    INTERVIEW = "INTERVIEW"
    FINAL_INTERVIEW = "FINAL_INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    CLOSED = "CLOSED"


class ApplicationChannel(str, enum.Enum):
    COMPANY_SITE = "COMPANY_SITE"
    JOB_PORTAL = "JOB_PORTAL"
    EMAIL = "EMAIL"
    REFERRAL = "REFERRAL"
    RECRUITER = "RECRUITER"
    TALENT_POOL = "TALENT_POOL"
    OFFLINE = "OFFLINE"
    OTHER = "OTHER"


class ApplicationPriority(str, enum.Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


class ApplicationStatusHistorySource(str, enum.Enum):
    USER = "USER"
    SYSTEM = "SYSTEM"
    EMAIL_CANDIDATE = "EMAIL_CANDIDATE"
    CALENDAR_SYNC = "CALENDAR_SYNC"


class ApplicationNoteType(str, enum.Enum):
    GENERAL = "GENERAL"
    CONTACT = "CONTACT"
    INTERVIEW = "INTERVIEW"
    DOCUMENT = "DOCUMENT"
    RESULT = "RESULT"
    REMINDER = "REMINDER"


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        Index("ix_applications_user_id", "user_id"),
        Index("ix_applications_user_status", "user_id", "status"),
        Index("ix_applications_user_applied_at", "user_id", "applied_at"),
        Index("ix_applications_user_updated_at", "user_id", "updated_at"),
        Index("ix_applications_user_archived", "user_id", "is_archived"),
        Index("ix_applications_job_id", "job_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("job_postings.id", ondelete="SET NULL"), nullable=True)
    resume_id: Mapped[int | None] = mapped_column(ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)
    resume_file_id: Mapped[int | None] = mapped_column(ForeignKey("resume_files.id", ondelete="SET NULL"), nullable=True)
    application_document_id: Mapped[int | None] = mapped_column(
        ForeignKey("application_documents.id", ondelete="SET NULL"), nullable=True
    )
    application_document_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("application_document_versions.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status"),
        nullable=False,
        default=ApplicationStatus.SAVED,
        server_default=ApplicationStatus.SAVED.value,
    )
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_apply_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    application_channel: Mapped[ApplicationChannel] = mapped_column(
        Enum(ApplicationChannel, name="application_channel"),
        nullable=False,
        default=ApplicationChannel.COMPANY_SITE,
        server_default=ApplicationChannel.COMPANY_SITE.value,
    )
    application_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    priority: Mapped[ApplicationPriority] = mapped_column(
        Enum(ApplicationPriority, name="application_priority"),
        nullable=False,
        default=ApplicationPriority.NORMAL,
        server_default=ApplicationPriority.NORMAL.value,
    )
    result_announced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    company_name_snapshot: Mapped[str | None] = mapped_column(String(160), nullable=True)
    job_title_snapshot: Mapped[str | None] = mapped_column(String(200), nullable=True)
    job_url_snapshot: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    job = relationship("JobPosting")
    resume = relationship("Resume")
    resume_file = relationship("ResumeFile")
    application_document = relationship("ApplicationDocument")
    application_document_version = relationship("ApplicationDocumentVersion")
    status_history = relationship("ApplicationStatusHistory", back_populates="application", cascade="all, delete-orphan")
    notes = relationship("ApplicationNote", back_populates="application", cascade="all, delete-orphan")


class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"
    __table_args__ = (
        Index("ix_application_status_history_application_created", "application_id", "created_at"),
        Index("ix_application_status_history_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    previous_status: Mapped[ApplicationStatus | None] = mapped_column(
        Enum(ApplicationStatus, name="application_status"), nullable=True
    )
    new_status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus, name="application_status"), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    reason: Mapped[str | None] = mapped_column(String(300), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[ApplicationStatusHistorySource] = mapped_column(
        Enum(ApplicationStatusHistorySource, name="application_status_history_source"),
        nullable=False,
        default=ApplicationStatusHistorySource.USER,
        server_default=ApplicationStatusHistorySource.USER.value,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    application = relationship("Application", back_populates="status_history")


class ApplicationNote(Base):
    __tablename__ = "application_notes"
    __table_args__ = (
        Index("ix_application_notes_application_created", "application_id", "created_at"),
        Index("ix_application_notes_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    note_type: Mapped[ApplicationNoteType] = mapped_column(
        Enum(ApplicationNoteType, name="application_note_type"),
        nullable=False,
        default=ApplicationNoteType.GENERAL,
        server_default=ApplicationNoteType.GENERAL.value,
    )
    is_pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    application = relationship("Application", back_populates="notes")
