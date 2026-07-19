from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class GmailToken:
    access_token: str
    refresh_token: str | None
    expires_at: datetime | None
    provider_account_id: str
    email: str | None
    display_name: str | None
    scopes: list[str]


@dataclass(frozen=True)
class GmailMessageRef:
    id: str
    thread_id: str | None = None


@dataclass(frozen=True)
class GmailMessage:
    id: str
    thread_id: str | None
    sender: str
    subject: str
    received_at: datetime
    snippet: str
    text: str


class GmailProvider(Protocol):
    def authorization_url(self, *, state: str, redirect_uri: str, scopes: list[str]) -> str: ...

    async def exchange_code(self, *, code: str, redirect_uri: str) -> GmailToken: ...

    async def refresh_token(self, *, refresh_token: str) -> GmailToken: ...

    async def revoke_token(self, *, token: str) -> None: ...

    async def search_messages(self, *, access_token: str, query: str, max_results: int) -> list[GmailMessageRef]: ...

    async def get_message(self, *, access_token: str, message_id: str) -> GmailMessage: ...
