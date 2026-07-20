import hashlib
from datetime import UTC, datetime

from app.notifications.providers.base import NotificationEmailResult


mock_notification_email_outbox: list[dict[str, str]] = []


def clear_mock_notification_email_outbox() -> None:
    mock_notification_email_outbox.clear()


class MockNotificationEmailProvider:
    provider = "mock"

    async def send(self, *, to: str, subject: str, body: str) -> NotificationEmailResult:
        seed = f"{to}|{subject}|{body}"
        message_id = f"mock-notification-{hashlib.sha256(seed.encode()).hexdigest()[:16]}"
        mock_notification_email_outbox.append(
            {
                "to": to,
                "subject": subject,
                "body": body,
                "message_id": message_id,
                "sent_at": datetime.now(UTC).isoformat(),
            }
        )
        return NotificationEmailResult(provider=self.provider, message_id=message_id)
