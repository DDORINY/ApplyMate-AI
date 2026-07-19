from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.schedule import (
    ScheduleConfidence,
    ScheduleEventStatus,
    ScheduleEventType,
    ScheduleHistoryAction,
    ScheduleHistorySource,
    ScheduleReminderStatus,
    ScheduleReminderType,
)
from app.schemas.application import ApplicationOptionItem
from app.schemas.job import clean_text


def validate_timezone(value: str) -> str:
    value = clean_text(value) or "Asia/Seoul"
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError("Invalid timezone.") from exc
    return value


def validate_online_url(value: str | None) -> str | None:
    value = clean_text(value)
    if value is None:
        return None
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Only http or https URL is allowed.")
    if parsed.username or parsed.password:
        raise ValueError("URL with credentials is not allowed.")
    return value


def ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Timezone-aware datetime is required.")
    return value.astimezone(UTC)


class ScheduleEventBase(BaseModel):
    application_id: int | None = None
    job_id: int | None = None
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    event_type: ScheduleEventType = ScheduleEventType.USER_EVENT
    status: ScheduleEventStatus = ScheduleEventStatus.SCHEDULED
    confidence: ScheduleConfidence = ScheduleConfidence.USER_INPUT
    start_at: datetime
    end_at: datetime
    all_day: bool = False
    timezone: str = Field(default="Asia/Seoul", max_length=64)
    location: str | None = Field(default=None, max_length=200)
    online_url: str | None = Field(default=None, max_length=1000)
    source: str | None = Field(default=None, max_length=120)
    source_reference: str | None = Field(default=None, max_length=500)
    confirmation_required: bool = False

    @field_validator("title")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        cleaned = clean_text(value)
        if not cleaned:
            raise ValueError("Title is required.")
        return cleaned

    @field_validator("description", "location", "source", "source_reference")
    @classmethod
    def trim_text_fields(cls, value: str | None) -> str | None:
        return clean_text(value)

    @field_validator("online_url")
    @classmethod
    def validate_url(cls, value: str | None) -> str | None:
        return validate_online_url(value)

    @field_validator("timezone")
    @classmethod
    def validate_timezone_field(cls, value: str) -> str:
        return validate_timezone(value)

    @field_validator("start_at", "end_at")
    @classmethod
    def validate_datetime(cls, value: datetime) -> datetime:
        return ensure_aware(value)

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.start_at >= self.end_at:
            raise ValueError("start_at must be before end_at.")
        return self


class ScheduleEventCreate(ScheduleEventBase):
    reminders: list["ScheduleReminderCreate"] = Field(default_factory=list)


class ScheduleEventUpdate(BaseModel):
    application_id: int | None = None
    job_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    event_type: ScheduleEventType | None = None
    status: ScheduleEventStatus | None = None
    confidence: ScheduleConfidence | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    all_day: bool | None = None
    timezone: str | None = Field(default=None, max_length=64)
    location: str | None = Field(default=None, max_length=200)
    online_url: str | None = Field(default=None, max_length=1000)
    source: str | None = Field(default=None, max_length=120)
    source_reference: str | None = Field(default=None, max_length=500)
    confirmation_required: bool | None = None

    @field_validator("title")
    @classmethod
    def trim_optional_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = clean_text(value)
        if not cleaned:
            raise ValueError("Title is required.")
        return cleaned

    @field_validator("description", "location", "source", "source_reference")
    @classmethod
    def trim_text_fields(cls, value: str | None) -> str | None:
        return clean_text(value)

    @field_validator("online_url")
    @classmethod
    def validate_url(cls, value: str | None) -> str | None:
        return validate_online_url(value)

    @field_validator("timezone")
    @classmethod
    def validate_timezone_field(cls, value: str | None) -> str | None:
        return validate_timezone(value) if value is not None else None

    @field_validator("start_at", "end_at")
    @classmethod
    def validate_datetime(cls, value: datetime | None) -> datetime | None:
        return ensure_aware(value) if value is not None else None


class ScheduleStatusChange(BaseModel):
    status: ScheduleEventStatus
    note: str | None = Field(default=None, max_length=1000)
    source: ScheduleHistorySource = ScheduleHistorySource.USER

    @field_validator("note")
    @classmethod
    def trim_note(cls, value: str | None) -> str | None:
        return clean_text(value)


class ScheduleReminderCreate(BaseModel):
    reminder_type: ScheduleReminderType = ScheduleReminderType.IN_APP
    minutes_before: int = Field(gt=0, le=60 * 24 * 30)


class ScheduleReminderUpdate(BaseModel):
    reminder_type: ScheduleReminderType | None = None
    minutes_before: int | None = Field(default=None, gt=0, le=60 * 24 * 30)
    status: ScheduleReminderStatus | None = None


class ScheduleReminderPublic(BaseModel):
    id: int
    event_id: int
    user_id: int
    reminder_type: ScheduleReminderType
    minutes_before: int
    scheduled_at: datetime
    status: ScheduleReminderStatus
    sent_at: datetime | None
    failed_at: datetime | None
    error_code: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScheduleConflictItem(BaseModel):
    id: int
    title: str
    event_type: ScheduleEventType
    status: ScheduleEventStatus
    start_at: datetime
    end_at: datetime


class ScheduleEventPublic(BaseModel):
    id: int
    user_id: int
    application_id: int | None
    job_id: int | None
    title: str
    description: str | None
    event_type: ScheduleEventType
    status: ScheduleEventStatus
    effective_status: ScheduleEventStatus
    confidence: ScheduleConfidence
    start_at: datetime
    end_at: datetime
    all_day: bool
    timezone: str
    location: str | None
    online_url: str | None
    source: str | None
    source_reference: str | None
    is_archived: bool
    completed_at: datetime | None
    cancelled_at: datetime | None
    confirmation_required: bool
    reminders_count: int = 0
    has_conflict: bool = False
    conflicting_events: list[ScheduleConflictItem] = Field(default_factory=list)
    is_overdue: bool = False
    is_due_soon: bool = False
    days_remaining: int | None = None
    hours_remaining: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScheduleEventListData(BaseModel):
    items: list[ScheduleEventPublic]
    page: int
    size: int
    total: int
    total_pages: int


class ScheduleEventHistoryPublic(BaseModel):
    id: int
    event_id: int
    user_id: int
    action: ScheduleHistoryAction
    previous_values: dict | None
    new_values: dict | None
    changed_fields: list | None
    source: ScheduleHistorySource
    created_at: datetime

    model_config = {"from_attributes": True}


class ScheduleOptionsData(BaseModel):
    event_types: list[str]
    statuses: list[str]
    confidences: list[str]
    reminder_types: list[str]
    reminder_presets: list[int]
    applications: list[ApplicationOptionItem]
    jobs: list[ApplicationOptionItem]


class ScheduleUpcomingData(BaseModel):
    items: list[ScheduleEventPublic]
    thresholds: list[int] = Field(default_factory=lambda: [24, 72, 168])


def reminder_scheduled_at(start_at: datetime, minutes_before: int) -> datetime:
    return start_at - timedelta(minutes=minutes_before)
