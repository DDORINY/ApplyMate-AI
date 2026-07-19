import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ScheduleEventType(str, enum.Enum):
    APPLICATION_DEADLINE = "APPLICATION_DEADLINE"
    DOCUMENT_RESULT = "DOCUMENT_RESULT"
    CODING_TEST = "CODING_TEST"
    ASSIGNMENT_DEADLINE = "ASSIGNMENT_DEADLINE"
    INTERVIEW = "INTERVIEW"
    FINAL_INTERVIEW = "FINAL_INTERVIEW"
    FINAL_RESULT = "FINAL_RESULT"
    OFFER_RESPONSE_DEADLINE = "OFFER_RESPONSE_DEADLINE"
    USER_EVENT = "USER_EVENT"


class ScheduleEventStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    MISSED = "MISSED"
    TENTATIVE = "TENTATIVE"


class ScheduleConfidence(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    ESTIMATED = "ESTIMATED"
    USER_INPUT = "USER_INPUT"
    AI_EXTRACTED = "AI_EXTRACTED"
    EMAIL_EXTRACTED = "EMAIL_EXTRACTED"


class ScheduleReminderType(str, enum.Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    PUSH = "PUSH"


class ScheduleReminderStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SENT = "SENT"
    FAILED = "FAILED"


class ScheduleHistoryAction(str, enum.Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    REMINDER_CHANGED = "REMINDER_CHANGED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class ScheduleHistorySource(str, enum.Enum):
    USER = "USER"
    SYSTEM = "SYSTEM"
    AI = "AI"
    EMAIL = "EMAIL"


class ScheduleEvent(Base):
    __tablename__ = "schedule_events"
    __table_args__ = (
        Index("ix_schedule_events_user_start", "user_id", "start_at"),
        Index("ix_schedule_events_user_status", "user_id", "status"),
        Index("ix_schedule_events_user_type", "user_id", "event_type"),
        Index("ix_schedule_events_user_archived", "user_id", "is_archived"),
        Index("ix_schedule_events_application_id", "application_id"),
        Index("ix_schedule_events_job_id", "job_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    application_id: Mapped[int | None] = mapped_column(ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("job_postings.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_type: Mapped[ScheduleEventType] = mapped_column(
        Enum(ScheduleEventType, name="schedule_event_type"),
        nullable=False,
        default=ScheduleEventType.USER_EVENT,
        server_default=ScheduleEventType.USER_EVENT.value,
    )
    status: Mapped[ScheduleEventStatus] = mapped_column(
        Enum(ScheduleEventStatus, name="schedule_event_status"),
        nullable=False,
        default=ScheduleEventStatus.SCHEDULED,
        server_default=ScheduleEventStatus.SCHEDULED.value,
    )
    confidence: Mapped[ScheduleConfidence] = mapped_column(
        Enum(ScheduleConfidence, name="schedule_confidence"),
        nullable=False,
        default=ScheduleConfidence.USER_INPUT,
        server_default=ScheduleConfidence.USER_INPUT.value,
    )
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    all_day: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Seoul", server_default="Asia/Seoul")
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    online_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmation_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    application = relationship("Application")
    job = relationship("JobPosting")
    reminders = relationship("ScheduleReminder", back_populates="event", cascade="all, delete-orphan")
    history = relationship("ScheduleEventHistory", back_populates="event", cascade="all, delete-orphan")


class ScheduleReminder(Base):
    __tablename__ = "schedule_reminders"
    __table_args__ = (
        Index("ix_schedule_reminders_event_id", "event_id"),
        Index("ix_schedule_reminders_user_scheduled", "user_id", "scheduled_at"),
        UniqueConstraint("event_id", "reminder_type", "minutes_before", name="uq_schedule_reminders_event_type_minutes"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("schedule_events.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reminder_type: Mapped[ScheduleReminderType] = mapped_column(
        Enum(ScheduleReminderType, name="schedule_reminder_type"),
        nullable=False,
        default=ScheduleReminderType.IN_APP,
        server_default=ScheduleReminderType.IN_APP.value,
    )
    minutes_before: Mapped[int] = mapped_column(Integer, nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[ScheduleReminderStatus] = mapped_column(
        Enum(ScheduleReminderStatus, name="schedule_reminder_status"),
        nullable=False,
        default=ScheduleReminderStatus.ACTIVE,
        server_default=ScheduleReminderStatus.ACTIVE.value,
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    event = relationship("ScheduleEvent", back_populates="reminders")


class ScheduleEventHistory(Base):
    __tablename__ = "schedule_event_history"
    __table_args__ = (
        Index("ix_schedule_event_history_event_created", "event_id", "created_at"),
        Index("ix_schedule_event_history_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("schedule_events.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[ScheduleHistoryAction] = mapped_column(Enum(ScheduleHistoryAction, name="schedule_history_action"), nullable=False)
    previous_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    changed_fields: Mapped[list | None] = mapped_column(JSON, nullable=True)
    source: Mapped[ScheduleHistorySource] = mapped_column(
        Enum(ScheduleHistorySource, name="schedule_history_source"),
        nullable=False,
        default=ScheduleHistorySource.USER,
        server_default=ScheduleHistorySource.USER.value,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    event = relationship("ScheduleEvent", back_populates="history")
