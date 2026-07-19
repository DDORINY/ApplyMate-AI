from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

from app.integrations.calendar.base import CalendarToken, ExternalCalendar, ExternalCalendarEvent
from app.models.schedule import ScheduleEvent


class MockCalendarProvider:
    def authorization_url(self, *, state: str, redirect_uri: str, scopes: list[str]) -> str:
        query = urlencode({"state": state, "code": "mock-calendar-code", "scope": " ".join(scopes)})
        return f"{redirect_uri}?{query}"

    async def exchange_code(self, *, code: str, redirect_uri: str) -> CalendarToken:
        return CalendarToken(
            provider_account_id="mock-google-calendar-account",
            email="calendar-user@example.com",
            display_name="Mock Calendar User",
            access_token=f"mock-access-credential-{code}",
            refresh_token="mock-refresh-credential",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            scopes=[],
        )

    async def refresh_token(self, *, refresh_token: str) -> CalendarToken:
        return CalendarToken(
            provider_account_id="mock-google-calendar-account",
            email="calendar-user@example.com",
            display_name="Mock Calendar User",
            access_token="mock-access-credential-refreshed",
            refresh_token=refresh_token,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            scopes=[],
        )

    async def revoke_token(self, *, token: str) -> None:
        return None

    async def list_calendars(self, *, access_token: str) -> list[ExternalCalendar]:
        return [
            ExternalCalendar(
                id="mock-primary",
                name="ApplyMate Mock Calendar",
                timezone="Asia/Seoul",
                primary=True,
                access_role="owner",
                writable=True,
            ),
            ExternalCalendar(
                id="mock-readonly",
                name="Read-only Mock Calendar",
                timezone="Asia/Seoul",
                primary=False,
                access_role="reader",
                writable=False,
            ),
        ]

    async def create_event(
        self, *, access_token: str, calendar_id: str, event: ScheduleEvent
    ) -> ExternalCalendarEvent:
        return self._event(calendar_id, event, f"mock-event-{event.id}")

    async def update_event(
        self, *, access_token: str, calendar_id: str, external_event_id: str, event: ScheduleEvent
    ) -> ExternalCalendarEvent:
        return self._event(calendar_id, event, external_event_id)

    async def delete_event(self, *, access_token: str, calendar_id: str, external_event_id: str) -> None:
        return None

    async def list_changes(
        self, *, access_token: str, calendar_id: str, sync_token: str | None
    ) -> list[ExternalCalendarEvent]:
        return []

    def _event(self, calendar_id: str, event: ScheduleEvent, external_event_id: str) -> ExternalCalendarEvent:
        updated_at = datetime.now(UTC)
        return ExternalCalendarEvent(
            id=external_event_id,
            etag=f"mock-etag-{calendar_id}-{event.id}-{int(updated_at.timestamp())}",
            updated_at=updated_at,
            status="confirmed",
            summary=event.title,
            html_link=f"https://calendar.example.com/{calendar_id}/{external_event_id}",
        )
