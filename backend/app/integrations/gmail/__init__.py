from app.core.config import get_settings
from app.core.exceptions import AppError
from app.integrations.gmail.base import GmailProvider
from app.integrations.gmail.google import GoogleGmailProvider
from app.integrations.gmail.mock import MockGmailProvider


def get_gmail_provider() -> GmailProvider:
    provider = get_settings().gmail_provider
    if provider == "mock":
        return MockGmailProvider()
    if provider == "google":
        return GoogleGmailProvider()
    raise AppError("GMAIL_PROVIDER_DISABLED", "Gmail provider is disabled.", 503)
