from urllib.parse import urlencode

import httpx

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.integrations.calendar.base import CalendarToken, ExternalCalendar, ExternalCalendarEvent
from app.models.schedule import ScheduleEvent


class GoogleCalendarProvider:
    authorization_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
    token_endpoint = "https://oauth2.googleapis.com/token"
    calendar_api_base = "https://www.googleapis.com/calendar/v3"

    def authorization_url(self, *, state: str, redirect_uri: str, scopes: list[str]) -> str:
        settings = get_settings()
        if not settings.google_calendar_client_id:
            raise AppError("CALENDAR_PROVIDER_DISABLED", "Google Calendar client id is not configured.", 503)
        query = urlencode(
            {
                "client_id": settings.google_calendar_client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": " ".join(scopes),
                "state": state,
                "access_type": "offline",
                "prompt": "consent",
            }
        )
        return f"{self.authorization_endpoint}?{query}"

    async def exchange_code(self, *, code: str, redirect_uri: str) -> CalendarToken:
        raise AppError(
            "CALENDAR_PROVIDER_UNAVAILABLE",
            "Real Google Calendar OAuth exchange requires operational credentials and manual verification.",
            503,
        )

    async def refresh_token(self, *, refresh_token: str) -> CalendarToken:
        raise AppError("CALENDAR_TOKEN_REFRESH_FAILED", "Google Calendar token refresh is not verified.", 503)

    async def revoke_token(self, *, token: str) -> None:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post("https://oauth2.googleapis.com/revoke", params={"token": token})

    async def list_calendars(self, *, access_token: str) -> list[ExternalCalendar]:
        raise AppError("CALENDAR_LIST_FAILED", "Real Google Calendar list requires manual verification.", 503)

    async def create_event(
        self, *, access_token: str, calendar_id: str, event: ScheduleEvent
    ) -> ExternalCalendarEvent:
        raise AppError("CALENDAR_SYNC_FAILED", "Real Google Calendar event creation is not verified.", 503)

    async def update_event(
        self, *, access_token: str, calendar_id: str, external_event_id: str, event: ScheduleEvent
    ) -> ExternalCalendarEvent:
        raise AppError("CALENDAR_SYNC_FAILED", "Real Google Calendar event update is not verified.", 503)

    async def delete_event(self, *, access_token: str, calendar_id: str, external_event_id: str) -> None:
        raise AppError("CALENDAR_SYNC_FAILED", "Real Google Calendar event deletion is not verified.", 503)

    async def list_changes(
        self, *, access_token: str, calendar_id: str, sync_token: str | None
    ) -> list[ExternalCalendarEvent]:
        raise AppError("CALENDAR_SYNC_FAILED", "Real Google Calendar incremental sync is not verified.", 503)
