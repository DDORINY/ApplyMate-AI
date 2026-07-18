import asyncio
import os
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ["JWT_SECRET_KEY"] = "test-access-secret"
os.environ["JWT_REFRESH_SECRET_KEY"] = "test-refresh-secret"
os.environ["GOOGLE_CLIENT_ID"] = "google-client"
os.environ["GOOGLE_CLIENT_SECRET"] = "google-secret"
os.environ["GOOGLE_REDIRECT_URI"] = "http://localhost:8000/api/v1/auth/oauth/google/callback"
os.environ["GITHUB_CLIENT_ID"] = "github-client"
os.environ["GITHUB_CLIENT_SECRET"] = "github-secret"
os.environ["GITHUB_REDIRECT_URI"] = "http://localhost:8000/api/v1/auth/oauth/github/callback"
os.environ["OAUTH_FRONTEND_CALLBACK_URL"] = "http://localhost:3000/auth/callback"
os.environ["OAUTH_ALLOWED_REDIRECT_PATHS"] = "/me,/profile,/settings/accounts"

from app.core.security import REFRESH_TOKEN_COOKIE_NAME
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models.oauth import OAuthAccount, OAuthProvider
from app.models.user import User
from app.services.oauth import OAuthProviderConfig, OAuthService, OAuthUserInfo


@pytest.fixture()
def client(monkeypatch):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    testing_session = async_sessionmaker(engine, expire_on_commit=False)

    async def init_db() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def dispose_db() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    async def override_get_session():
        async with testing_session() as session:
            yield session

    asyncio.run(init_db())
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        test_client.testing_session = testing_session
        yield test_client

    app.dependency_overrides.clear()
    asyncio.run(dispose_db())


class FakeAdapter:
    def __init__(self, user_info: OAuthUserInfo) -> None:
        self.user_info = user_info

    def authorization_url(self, state: str) -> str:
        return f"https://provider.example/oauth?state={state}"

    async def fetch_user_info(self, _code: str) -> OAuthUserInfo:
        return self.user_info


def fake_google_user(email: str = "social@example.com", provider_user_id: str = "google-1"):
    return OAuthUserInfo(
        provider=OAuthProvider.GOOGLE,
        provider_user_id=provider_user_id,
        email=email,
        email_verified=True,
        username=email,
        display_name="Social User",
    )


def patch_adapter(monkeypatch, user_info: OAuthUserInfo) -> None:
    monkeypatch.setattr(
        OAuthService, "get_adapter", lambda _self, _provider: FakeAdapter(user_info)
    )


def extract_state(authorization_url: str) -> str:
    return parse_qs(urlparse(authorization_url).query)["state"][0]


def extract_callback_param(callback_url: str, key: str) -> str:
    return parse_qs(urlparse(callback_url).query)[key][0]


async def get_user(testing_session, email: str) -> User:
    async with testing_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one()


async def count_oauth_accounts(testing_session) -> int:
    async with testing_session() as session:
        result = await session.execute(select(OAuthAccount))
        return len(list(result.scalars()))


def signup_and_login(client: TestClient, email: str = "owner@example.com") -> str:
    client.post(
        "/api/v1/auth/signup",
        json={"name": "Owner", "email": email, "password": "password123"},
    )
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return response.json()["data"]["access_token"]


def test_oauth_providers_are_listed(client, monkeypatch):
    def provider_config(_self, provider: OAuthProvider) -> OAuthProviderConfig:
        return OAuthProviderConfig(
            provider=provider,
            client_id=f"{provider.value.lower()}-client",
            client_secret=f"{provider.value.lower()}-secret",
            redirect_uri=f"http://localhost:8000/{provider.value.lower()}/callback",
            scope="email",
        )

    monkeypatch.setattr(OAuthService, "provider_config", provider_config)

    response = client.get("/api/v1/auth/oauth/providers")

    assert response.status_code == 200
    providers = response.json()["data"]["providers"]
    assert providers == [
        {"provider": "GOOGLE", "enabled": True},
        {"provider": "GITHUB", "enabled": True},
    ]


def test_oauth_authorize_rejects_unapproved_redirect(client):
    response = client.get("/api/v1/auth/oauth/google/authorize?redirect_path=https://evil.example")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "OAUTH_REDIRECT_NOT_ALLOWED"


def test_oauth_callback_creates_social_user_and_exchange_issues_tokens(client, monkeypatch):
    patch_adapter(monkeypatch, fake_google_user())

    authorize = client.get("/api/v1/auth/oauth/google/authorize?redirect_path=/me")
    state = extract_state(authorize.json()["data"]["authorization_url"])

    callback = client.get(
        f"/api/v1/auth/oauth/google/callback?code=ok&state={state}", follow_redirects=False
    )
    assert callback.status_code == 302
    ticket = extract_callback_param(callback.headers["location"], "ticket")

    exchange = client.post("/api/v1/auth/oauth/exchange", json={"ticket": ticket})

    assert exchange.status_code == 200
    assert exchange.json()["data"]["user"]["email"] == "social@example.com"
    assert exchange.json()["data"]["user"]["email_verified"] is True
    assert REFRESH_TOKEN_COOKIE_NAME in exchange.cookies
    user = asyncio.run(get_user(client.testing_session, "social@example.com"))
    assert user.password_hash is None
    assert asyncio.run(count_oauth_accounts(client.testing_session)) == 1


def test_oauth_ticket_can_be_exchanged_once(client, monkeypatch):
    patch_adapter(monkeypatch, fake_google_user(provider_user_id="google-once"))
    authorize = client.get("/api/v1/auth/oauth/google/authorize?redirect_path=/me")
    state = extract_state(authorize.json()["data"]["authorization_url"])
    callback = client.get(
        f"/api/v1/auth/oauth/google/callback?code=ok&state={state}", follow_redirects=False
    )
    ticket = extract_callback_param(callback.headers["location"], "ticket")

    assert client.post("/api/v1/auth/oauth/exchange", json={"ticket": ticket}).status_code == 200
    reused = client.post("/api/v1/auth/oauth/exchange", json={"ticket": ticket})

    assert reused.status_code == 401
    assert reused.json()["error"]["code"] == "OAUTH_TICKET_INVALID"


def test_existing_email_requires_explicit_account_link(client, monkeypatch):
    signup_and_login(client, "social@example.com")
    patch_adapter(monkeypatch, fake_google_user())
    authorize = client.get("/api/v1/auth/oauth/google/authorize?redirect_path=/me")
    state = extract_state(authorize.json()["data"]["authorization_url"])

    callback = client.get(
        f"/api/v1/auth/oauth/google/callback?code=ok&state={state}", follow_redirects=False
    )

    assert callback.status_code == 302
    assert (
        extract_callback_param(callback.headers["location"], "error")
        == "OAUTH_ACCOUNT_LINK_REQUIRED"
    )


def test_authenticated_user_can_link_list_and_unlink_social_account(client, monkeypatch):
    access_token = signup_and_login(client)
    patch_adapter(
        monkeypatch, fake_google_user(email="owner@example.com", provider_user_id="owner-google")
    )

    authorize = client.get(
        "/api/v1/auth/oauth/google/link/authorize?redirect_path=/settings/accounts",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    state = extract_state(authorize.json()["data"]["authorization_url"])
    callback = client.get(
        f"/api/v1/auth/oauth/google/callback?code=ok&state={state}", follow_redirects=False
    )

    assert callback.status_code == 302
    accounts = client.get(
        "/api/v1/auth/oauth/accounts",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert accounts.status_code == 200
    assert accounts.json()["data"]["accounts"][0]["provider"] == "GOOGLE"

    deleted = client.delete(
        "/api/v1/auth/oauth/accounts/google",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert deleted.status_code == 200
    assert deleted.json()["data"] == {"unlinked": True}
