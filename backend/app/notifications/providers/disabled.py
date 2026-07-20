from app.core.exceptions import AppError
from app.notifications.providers.base import NotificationEmailResult


class DisabledNotificationEmailProvider:
    provider = "disabled"

    async def send(self, *, to: str, subject: str, body: str) -> NotificationEmailResult:
        raise AppError("NOTIFICATION_PROVIDER_DISABLED", "알림 이메일 provider가 비활성화되어 있습니다.", 503)
