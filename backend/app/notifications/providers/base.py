from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class NotificationEmailResult:
    provider: str
    message_id: str | None


class NotificationEmailProvider(Protocol):
    provider: str

    async def send(self, *, to: str, subject: str, body: str) -> NotificationEmailResult:
        ...
