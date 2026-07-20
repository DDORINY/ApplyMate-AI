from datetime import datetime, time
from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.models.notification import (
    NotificationChannel,
    NotificationDeliveryStatus,
    NotificationEventType,
    NotificationPriority,
    NotificationProcessingRunStatus,
    NotificationProcessingTaskType,
    NotificationStatus,
)


class NotificationSettingUpdate(BaseModel):
    in_app_enabled: bool | None = None
    email_enabled: bool | None = None
    push_enabled: bool | None = None
    timezone: str | None = Field(default=None, max_length=64)
    quiet_hours_enabled: bool | None = None
    quiet_hours_start: time | None = None
    quiet_hours_end: time | None = None
    schedule_reminder_enabled: bool | None = None
    application_deadline_enabled: bool | None = None
    recommendation_enabled: bool | None = None
    gmail_candidate_enabled: bool | None = None
    document_improvement_enabled: bool | None = None
    sync_error_enabled: bool | None = None
    default_reminder_minutes: int | None = Field(default=None, ge=1, le=10080)
    daily_digest_enabled: bool | None = None
    daily_digest_hour: int | None = Field(default=None, ge=0, le=23)

    @model_validator(mode="after")
    def validate_quiet_hours(self):
        if self.quiet_hours_enabled and (self.quiet_hours_start is None or self.quiet_hours_end is None):
            raise ValueError("quiet hours start and end are required when quiet hours are enabled")
        return self


class NotificationSettingPublic(BaseModel):
    id: int
    user_id: int
    in_app_enabled: bool
    email_enabled: bool
    push_enabled: bool
    timezone: str
    quiet_hours_enabled: bool
    quiet_hours_start: time | None
    quiet_hours_end: time | None
    schedule_reminder_enabled: bool
    application_deadline_enabled: bool
    recommendation_enabled: bool
    gmail_candidate_enabled: bool
    document_improvement_enabled: bool
    sync_error_enabled: bool
    default_reminder_minutes: int
    daily_digest_enabled: bool
    daily_digest_hour: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotificationPublic(BaseModel):
    id: int
    user_id: int
    event_type: NotificationEventType
    priority: NotificationPriority
    status: NotificationStatus
    title: str
    message: str
    source_type: str
    source_id: str
    source_url: str | None
    deduplication_key: str
    payload: dict[str, Any] | None
    scheduled_for: datetime | None
    read_at: datetime | None
    dismissed_at: datetime | None
    archived_at: datetime | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotificationListData(BaseModel):
    items: list[NotificationPublic]
    page: int
    size: int
    total: int
    total_pages: int


class NotificationUnreadCountData(BaseModel):
    unread_count: int


class NotificationDeliveryPublic(BaseModel):
    id: int
    notification_id: int
    user_id: int
    channel: NotificationChannel
    status: NotificationDeliveryStatus
    provider: str
    attempt_count: int
    next_retry_at: datetime | None
    sent_at: datetime | None
    provider_message_id: str | None
    error_code: str | None
    safe_error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotificationDeliveryListData(BaseModel):
    items: list[NotificationDeliveryPublic]
    page: int
    size: int
    total: int
    total_pages: int


class NotificationProcessingRunPublic(BaseModel):
    id: int
    task_type: NotificationProcessingTaskType
    status: NotificationProcessingRunStatus
    started_at: datetime
    completed_at: datetime | None
    processed_count: int
    created_count: int
    sent_count: int
    failed_count: int
    skipped_count: int
    error_code: str | None
    safe_error_message: str | None
    result: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}
