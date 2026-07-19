from datetime import datetime

from pydantic import BaseModel, Field

from app.models.integration import CalendarConnectionStatus, CalendarSyncDirection, CalendarSyncStatus, SyncRunStatus


class CalendarConnectRequest(BaseModel):
    redirect_path: str = Field(default="/settings/integrations", max_length=255)


class CalendarConnectData(BaseModel):
    authorization_url: str
    state: str
    provider: str
    scopes: list[str]


class CalendarCallbackData(BaseModel):
    connected: bool
    connection_id: int
    provider: str
    email: str | None


class CalendarIntegrationStatusData(BaseModel):
    connected: bool
    provider: str
    email: str | None = None
    display_name: str | None = None
    scopes: list[str] = Field(default_factory=list)
    selected_calendar_id: str | None = None
    selected_calendar_name: str | None = None
    selected_calendar_timezone: str | None = None
    sync_direction: CalendarSyncDirection | None = None
    sync_enabled: bool = False
    status: CalendarConnectionStatus | None = None
    last_sync_at: datetime | None = None
    needs_verification: bool = False


class ExternalCalendarPublic(BaseModel):
    id: str
    name: str
    timezone: str
    primary: bool
    access_role: str
    writable: bool
    selected: bool = False


class CalendarSettingsUpdate(BaseModel):
    selected_calendar_id: str | None = Field(default=None, max_length=500)
    sync_direction: CalendarSyncDirection | None = None
    sync_enabled: bool | None = None


class CalendarSyncMappingPublic(BaseModel):
    id: int
    schedule_event_id: int
    external_calendar_id: str
    external_event_id: str
    external_etag: str | None
    sync_status: CalendarSyncStatus
    last_synced_at: datetime | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class CalendarSyncRunPublic(BaseModel):
    id: int
    direction: CalendarSyncDirection
    status: SyncRunStatus
    started_at: datetime
    completed_at: datetime | None
    created_count: int
    updated_count: int
    deleted_count: int
    skipped_count: int
    conflict_count: int
    error_count: int

    model_config = {"from_attributes": True}


class CalendarSyncErrorPublic(BaseModel):
    id: int
    sync_run_id: int | None
    mapping_id: int | None
    error_code: str
    safe_message: str
    retryable: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CalendarSyncResult(BaseModel):
    run: CalendarSyncRunPublic
    mappings: list[CalendarSyncMappingPublic] = Field(default_factory=list)
    errors: list[CalendarSyncErrorPublic] = Field(default_factory=list)


class EventSyncStatusData(BaseModel):
    connected: bool
    mapping: CalendarSyncMappingPublic | None = None
    last_error: CalendarSyncErrorPublic | None = None
