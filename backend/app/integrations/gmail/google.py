from urllib.parse import urlencode

import httpx

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.integrations.gmail.base import GmailMessage, GmailMessageRef, GmailToken


class GoogleGmailProvider:
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"

    def authorization_url(self, *, state: str, redirect_uri: str, scopes: list[str]) -> str:
        settings = get_settings()
        query = urlencode(
            {
                "client_id": settings.google_gmail_client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": " ".join(scopes),
                "access_type": "offline",
                "prompt": "consent",
                "state": state,
            }
        )
        return f"{self.AUTH_URL}?{query}"

    async def exchange_code(self, *, code: str, redirect_uri: str) -> GmailToken:
        raise AppError("GMAIL_PROVIDER_UNAVAILABLE", "Real Gmail OAuth token exchange is NEEDS_VERIFICATION.", 503)

    async def refresh_token(self, *, refresh_token: str) -> GmailToken:
        raise AppError("GMAIL_TOKEN_REFRESH_FAILED", "Real Gmail token refresh is NEEDS_VERIFICATION.", 503)

    async def revoke_token(self, *, token: str) -> None:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post("https://oauth2.googleapis.com/revoke", data={"token": token})

    async def search_messages(self, *, access_token: str, query: str, max_results: int) -> list[GmailMessageRef]:
        raise AppError("GMAIL_PROVIDER_UNAVAILABLE", "Real Gmail message search is NEEDS_VERIFICATION.", 503)

    async def get_message(self, *, access_token: str, message_id: str) -> GmailMessage:
        raise AppError("GMAIL_PROVIDER_UNAVAILABLE", "Real Gmail message fetch is NEEDS_VERIFICATION.", 503)
