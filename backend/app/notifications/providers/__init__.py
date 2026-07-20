from app.core.config import settings
from app.notifications.providers.base import NotificationEmailProvider
from app.notifications.providers.disabled import DisabledNotificationEmailProvider
from app.notifications.providers.mock import MockNotificationEmailProvider
from app.notifications.providers.smtp import SmtpNotificationEmailProvider


def get_notification_email_provider() -> NotificationEmailProvider:
    provider = settings.email_provider.strip().lower()
    if provider in {"development", "mock"}:
        return MockNotificationEmailProvider()
    if provider == "smtp":
        return SmtpNotificationEmailProvider()
    return DisabledNotificationEmailProvider()
