from app.notifications.providers.base import NotificationEmailResult
from app.services.email import get_email_sender


class SmtpNotificationEmailProvider:
    provider = "smtp"

    async def send(self, *, to: str, subject: str, body: str) -> NotificationEmailResult:
        await get_email_sender().send(to, subject, body)
        return NotificationEmailResult(provider=self.provider, message_id=None)
