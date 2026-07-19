from app.core.config import get_settings
from app.core.exceptions import AppError
from app.integrations.calendar.base import CalendarProvider
from app.integrations.calendar.google import GoogleCalendarProvider
from app.integrations.calendar.mock import MockCalendarProvider


def get_calendar_provider() -> CalendarProvider:
    provider = get_settings().calendar_provider
    if provider == "mock":
        return MockCalendarProvider()
    if provider == "google":
        return GoogleCalendarProvider()
    raise AppError("CALENDAR_PROVIDER_DISABLED", "Calendar provider is disabled.", 503)
