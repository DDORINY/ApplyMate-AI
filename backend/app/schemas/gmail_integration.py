from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.email_analysis import (
    EmailCandidateStatus,
    EmailCandidateType,
    EmailProcessingStatus,
    EmailSyncRunStatus,
    GmailConnectionStatus,
)
from app.models.application import ApplicationStatus


class GmailConnectRequest(BaseModel):
    redirect_path: str = "/settings/integrations"


class GmailConnectData(BaseModel):
    authorization_url: str
    state: str
    provider: str
    scopes: list[str]


class GmailCallbackData(BaseModel):
    connected: bool
    connection_id: int
    provider: str
    email: str | None = None


class GmailIntegrationStatusData(BaseModel):
    connected: bool
    provider: str
    email: str | None = None
    display_name: str | None = None
    scopes: list[str] = Field(default_factory=list)
    status: GmailConnectionStatus | None = None
    sync_enabled: bool = False
    search_query: str | None = None
    lookback_days: int | None = None
    last_sync_at: datetime | None = None
    needs_verification: bool = False


class GmailSettingsUpdate(BaseModel):
    sync_enabled: bool | None = None
    search_query: str | None = Field(default=None, min_length=1, max_length=1000)
    lookback_days: int | None = Field(default=None, ge=1, le=90)


class EmailSyncRunPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: EmailSyncRunStatus
    started_at: datetime
    completed_at: datetime | None
    scanned_count: int
    matched_count: int
    candidate_count: int
    ignored_count: int
    error_count: int


class EmailMessagePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_message_id: str
    provider_thread_id: str | None
    sender: str
    sender_domain: str | None
    subject: str
    received_at: datetime
    snippet: str | None
    processing_status: EmailProcessingStatus
    classification: str | None
    confidence: int


class EmailCandidatePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email_message_id: int
    candidate_type: EmailCandidateType
    status: EmailCandidateStatus
    company_name: str | None
    job_title: str | None
    application_id: int | None
    event_payload: dict[str, Any] | None
    status_payload: dict[str, Any] | None
    confidence: int
    evidence: dict[str, Any]
    requires_review: bool
    review_reason: str | None
    expires_at: datetime | None
    created_at: datetime
    email_message: EmailMessagePublic | None = None


class EmailCandidateListData(BaseModel):
    items: list[EmailCandidatePublic]
    total: int
    page: int
    size: int


class EmailCandidateApproveRequest(BaseModel):
    apply_status_change: bool = False
    create_schedule_event: bool = False
    application_id: int | None = None


class EmailCandidateRejectRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class EmailCandidateApplicationOption(BaseModel):
    id: int
    company_name: str | None
    job_title: str | None
    status: ApplicationStatus
    match_type: str
    evidence: list[str]


class EmailCandidateApplicationOptionsData(BaseModel):
    items: list[EmailCandidateApplicationOption]


class EmailCandidateActionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: str
    application_id: int | None
    schedule_event_id: int | None
    previous_values: dict[str, Any] | None
    new_values: dict[str, Any] | None
    created_at: datetime


class EmailCandidateApproveData(BaseModel):
    candidate: EmailCandidatePublic
    actions: list[EmailCandidateActionPublic]


class GmailSyncResult(BaseModel):
    run: EmailSyncRunPublic
    candidates: list[EmailCandidatePublic]
