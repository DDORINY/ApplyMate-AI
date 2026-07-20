import enum
from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, JSON, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NotificationEventType(str, enum.Enum):
    SCHEDULE_REMINDER = "SCHEDULE_REMINDER"
    APPLICATION_DEADLINE = "APPLICATION_DEADLINE"
    INTERVIEW_REMINDER = "INTERVIEW_REMINDER"
    ASSESSMENT_DEADLINE = "ASSESSMENT_DEADLINE"
    JOB_RECOMMENDATION_NEW = "JOB_RECOMMENDATION_NEW"
    JOB_RECOMMENDATION_SCORE_UP = "JOB_RECOMMENDATION_SCORE_UP"
    GMAIL_CANDIDATE_CREATED = "GMAIL_CANDIDATE_CREATED"
    APPLICATION_STATUS_CHANGED = "APPLICATION_STATUS_CHANGED"
    DOCUMENT_IMPROVEMENT_COMPLETED = "DOCUMENT_IMPROVEMENT_COMPLETED"
    DOCUMENT_IMPROVEMENT_FAILED = "DOCUMENT_IMPROVEMENT_FAILED"
    CALENDAR_SYNC_FAILED = "CALENDAR_SYNC_FAILED"
    GMAIL_SYNC_FAILED = "GMAIL_SYNC_FAILED"
    SYSTEM = "SYSTEM"


class NotificationChannel(str, enum.Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    PUSH = "PUSH"


class NotificationStatus(str, enum.Enum):
    UNREAD = "UNREAD"
    READ = "READ"
    DISMISSED = "DISMISSED"
    ARCHIVED = "ARCHIVED"
    EXPIRED = "EXPIRED"


class NotificationPriority(str, enum.Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


class NotificationDeliveryStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    FAILED = "FAILED"
    RETRY_SCHEDULED = "RETRY_SCHEDULED"
    CANCELLED = "CANCELLED"
    SKIPPED = "SKIPPED"


class NotificationProcessingTaskType(str, enum.Enum):
    PROCESS_DUE_SCHEDULE_REMINDERS = "PROCESS_DUE_SCHEDULE_REMINDERS"
    PROCESS_RECOMMENDATION_NOTIFICATION_CANDIDATES = "PROCESS_RECOMMENDATION_NOTIFICATION_CANDIDATES"
    PROCESS_GMAIL_CANDIDATES = "PROCESS_GMAIL_CANDIDATES"
    PROCESS_DOCUMENT_IMPROVEMENTS = "PROCESS_DOCUMENT_IMPROVEMENTS"
    PROCESS_SYNC_FAILURES = "PROCESS_SYNC_FAILURES"
    PROCESS_PENDING_EMAIL_DELIVERIES = "PROCESS_PENDING_EMAIL_DELIVERIES"
    RETRY_FAILED_DELIVERIES = "RETRY_FAILED_DELIVERIES"
    EXPIRE_OLD_NOTIFICATIONS = "EXPIRE_OLD_NOTIFICATIONS"
    RUN_DUE_NOTIFICATIONS = "RUN_DUE_NOTIFICATIONS"


class NotificationProcessingRunStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL_FAILED = "PARTIAL_FAILED"


class NotificationSetting(Base):
    __tablename__ = "notification_settings"
    __table_args__ = (UniqueConstraint("user_id", name="uq_notification_settings_user_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    email_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    push_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Seoul", server_default="Asia/Seoul")
    quiet_hours_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    quiet_hours_start: Mapped[time | None] = mapped_column(Time(timezone=False), nullable=True)
    quiet_hours_end: Mapped[time | None] = mapped_column(Time(timezone=False), nullable=True)
    schedule_reminder_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    application_deadline_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    recommendation_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    gmail_candidate_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    document_improvement_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    sync_error_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    default_reminder_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30, server_default="30")
    daily_digest_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    daily_digest_hour: Mapped[int] = mapped_column(Integer, nullable=False, default=9, server_default="9")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        UniqueConstraint("deduplication_key", name="uq_notifications_deduplication_key"),
        Index("ix_notifications_user_status_created", "user_id", "status", "created_at"),
        Index("ix_notifications_user_event", "user_id", "event_type"),
        Index("ix_notifications_scheduled", "scheduled_for"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[NotificationEventType] = mapped_column(Enum(NotificationEventType, name="notification_event_type"), nullable=False)
    priority: Mapped[NotificationPriority] = mapped_column(
        Enum(NotificationPriority, name="notification_priority"),
        nullable=False,
        default=NotificationPriority.NORMAL,
        server_default=NotificationPriority.NORMAL.value,
    )
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, name="notification_status"),
        nullable=False,
        default=NotificationStatus.UNREAD,
        server_default=NotificationStatus.UNREAD.value,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source_id: Mapped[str] = mapped_column(String(120), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    deduplication_key: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dismissed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    deliveries = relationship("NotificationDelivery", back_populates="notification", cascade="all, delete-orphan")


class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"
    __table_args__ = (
        UniqueConstraint("notification_id", "channel", name="uq_notification_deliveries_notification_channel"),
        Index("ix_notification_deliveries_user_status", "user_id", "status"),
        Index("ix_notification_deliveries_next_retry", "next_retry_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notification_id: Mapped[int] = mapped_column(ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(Enum(NotificationChannel, name="notification_channel"), nullable=False)
    status: Mapped[NotificationDeliveryStatus] = mapped_column(
        Enum(NotificationDeliveryStatus, name="notification_delivery_status"),
        nullable=False,
        default=NotificationDeliveryStatus.PENDING,
        server_default=NotificationDeliveryStatus.PENDING.value,
    )
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    safe_error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    notification = relationship("Notification", back_populates="deliveries")


class NotificationProcessingRun(Base):
    __tablename__ = "notification_processing_runs"
    __table_args__ = (
        Index("ix_notification_processing_runs_task_created", "task_type", "created_at"),
        Index("ix_notification_processing_runs_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_type: Mapped[NotificationProcessingTaskType] = mapped_column(Enum(NotificationProcessingTaskType, name="notification_processing_task_type"), nullable=False)
    status: Mapped[NotificationProcessingRunStatus] = mapped_column(Enum(NotificationProcessingRunStatus, name="notification_processing_run_status"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    sent_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    skipped_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    safe_error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
