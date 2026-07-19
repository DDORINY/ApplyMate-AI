from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.models.schedule import ScheduleEvent


@dataclass(frozen=True)
class CalendarToken:
    provider_account_id: str
    email: str | None
    display_name: str | None
    access_token: str
    refresh_token: str | None
    expires_at: datetime | None
    scopes: list[str]


@dataclass(frozen=True)
class ExternalCalendar:
    id: str
    name: str
    timezone: str
    primary: bool
    access_role: str
    writable: bool


@dataclass(frozen=True)
class ExternalCalendarEvent:
    id: str
    etag: str | None
    updated_at: datetime | None
    status: str
    summary: str
    html_link: str | None = None


class CalendarProvider(Protocol):
    def authorization_url(self, *, state: str, redirect_uri: str, scopes: list[str]) -> str:
        """Build provider authorization URL."""

    async def exchange_code(self, *, code: str, redirect_uri: str) -> CalendarToken:
        """Exchange OAuth code for token data."""

    async def refresh_token(self, *, refresh_token: str) -> CalendarToken:
        """Refresh provider token."""

    async def revoke_token(self, *, token: str) -> None:
        """Revoke provider token."""

    async def list_calendars(self, *, access_token: str) -> list[ExternalCalendar]:
        """List calendars."""

    async def create_event(
        self, *, access_token: str, calendar_id: str, event: ScheduleEvent
    ) -> ExternalCalendarEvent:
        """Create provider event."""

    async def update_event(
        self, *, access_token: str, calendar_id: str, external_event_id: str, event: ScheduleEvent
    ) -> ExternalCalendarEvent:
        """Update provider event."""

    async def delete_event(self, *, access_token: str, calendar_id: str, external_event_id: str) -> None:
        """Delete provider event."""

    async def list_changes(self, *, access_token: str, calendar_id: str, sync_token: str | None) -> list[ExternalCalendarEvent]:
        """List changed provider events."""
