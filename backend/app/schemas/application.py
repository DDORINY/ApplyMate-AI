from datetime import datetime
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator

from app.models.application import (
    ApplicationChannel,
    ApplicationNoteType,
    ApplicationPriority,
    ApplicationStatus,
    ApplicationStatusHistorySource,
)
from app.schemas.job import clean_text


def validate_http_url(value: str | None) -> str | None:
    value = clean_text(value)
    if value is None:
        return None
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("http 또는 https URL만 사용할 수 있습니다.")
    if parsed.username or parsed.password:
        raise ValueError("인증정보가 포함된 URL은 사용할 수 없습니다.")
    return value


class ApplicationCreate(BaseModel):
    job_id: int | None = None
    resume_id: int | None = None
    resume_file_id: int | None = None
    application_document_id: int | None = None
    application_document_version_id: int | None = None
    status: ApplicationStatus = ApplicationStatus.SAVED
    applied_at: datetime | None = None
    planned_apply_at: datetime | None = None
    application_channel: ApplicationChannel = ApplicationChannel.COMPANY_SITE
    application_url: str | None = Field(default=None, max_length=1000)
    contact_name: str | None = Field(default=None, max_length=120)
    contact_email: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=80)
    source: str | None = Field(default=None, max_length=120)
    priority: ApplicationPriority = ApplicationPriority.NORMAL
    result_announced_at: datetime | None = None
    closed_at: datetime | None = None

    @field_validator("application_url")
    @classmethod
    def validate_application_url(cls, value: str | None) -> str | None:
        return validate_http_url(value)

    @field_validator("contact_name", "contact_email", "contact_phone", "source")
    @classmethod
    def trim_text_fields(cls, value: str | None) -> str | None:
        return clean_text(value)


class ApplicationUpdate(BaseModel):
    job_id: int | None = None
    resume_id: int | None = None
    resume_file_id: int | None = None
    application_document_id: int | None = None
    application_document_version_id: int | None = None
    applied_at: datetime | None = None
    planned_apply_at: datetime | None = None
    application_channel: ApplicationChannel | None = None
    application_url: str | None = Field(default=None, max_length=1000)
    contact_name: str | None = Field(default=None, max_length=120)
    contact_email: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=80)
    source: str | None = Field(default=None, max_length=120)
    priority: ApplicationPriority | None = None
    result_announced_at: datetime | None = None
    closed_at: datetime | None = None

    @field_validator("application_url")
    @classmethod
    def validate_application_url(cls, value: str | None) -> str | None:
        return validate_http_url(value)

    @field_validator("contact_name", "contact_email", "contact_phone", "source")
    @classmethod
    def trim_text_fields(cls, value: str | None) -> str | None:
        return clean_text(value)


class ApplicationStatusChange(BaseModel):
    status: ApplicationStatus
    reason: str | None = Field(default=None, max_length=300)
    note: str | None = Field(default=None, max_length=2000)
    source: ApplicationStatusHistorySource = ApplicationStatusHistorySource.USER
    changed_at: datetime | None = None

    @field_validator("reason", "note")
    @classmethod
    def trim_text_fields(cls, value: str | None) -> str | None:
        return clean_text(value)


class ApplicationNoteCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
    note_type: ApplicationNoteType = ApplicationNoteType.GENERAL
    is_pinned: bool = False

    @field_validator("content")
    @classmethod
    def trim_content(cls, value: str) -> str:
        cleaned = clean_text(value)
        if not cleaned:
            raise ValueError("메모 내용을 입력해 주세요.")
        return cleaned


class ApplicationNoteUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=5000)
    note_type: ApplicationNoteType | None = None
    is_pinned: bool | None = None

    @field_validator("content")
    @classmethod
    def trim_content(cls, value: str | None) -> str | None:
        return clean_text(value)


class ApplicationPublic(BaseModel):
    id: int
    user_id: int
    job_id: int | None
    resume_id: int | None
    resume_file_id: int | None
    application_document_id: int | None
    application_document_version_id: int | None
    status: ApplicationStatus
    applied_at: datetime | None
    planned_apply_at: datetime | None
    application_channel: ApplicationChannel
    application_url: str | None
    contact_name: str | None
    contact_email: str | None
    contact_phone: str | None
    source: str | None
    priority: ApplicationPriority
    result_announced_at: datetime | None
    closed_at: datetime | None
    company_name_snapshot: str | None
    job_title_snapshot: str | None
    job_url_snapshot: str | None
    is_archived: bool
    archived_at: datetime | None
    notes_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApplicationListData(BaseModel):
    items: list[ApplicationPublic]
    page: int
    size: int
    total: int
    total_pages: int


class ApplicationStatusHistoryPublic(BaseModel):
    id: int
    application_id: int
    user_id: int
    previous_status: ApplicationStatus | None
    new_status: ApplicationStatus
    changed_at: datetime
    reason: str | None
    note: str | None
    source: ApplicationStatusHistorySource
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplicationNotePublic(BaseModel):
    id: int
    application_id: int
    user_id: int
    content: str
    note_type: ApplicationNoteType
    is_pinned: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApplicationOptionItem(BaseModel):
    id: int
    label: str
    description: str | None = None
    disabled_reason: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class ApplicationOptionsData(BaseModel):
    jobs: list[ApplicationOptionItem]
    resumes: list[ApplicationOptionItem]
    resume_files: list[ApplicationOptionItem]
    resume_analyses: list[ApplicationOptionItem]
    job_analyses: list[ApplicationOptionItem]
    job_matches: list[ApplicationOptionItem]
    application_documents: list[ApplicationOptionItem]
    application_document_versions: list[ApplicationOptionItem]
