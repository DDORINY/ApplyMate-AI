import asyncio
import os
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ["JWT_SECRET_KEY"] = "test-access-secret"
os.environ["JWT_REFRESH_SECRET_KEY"] = "test-refresh-secret"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "14"
os.environ["EMAIL_PROVIDER"] = "development"
os.environ["LOGIN_MAX_FAILED_ATTEMPTS"] = "3"

from app.core.security import (  # noqa: E402
    REFRESH_TOKEN_COOKIE_NAME,
    create_jwt,
    hash_token,
)
from app.db.base import Base  # noqa: E402
from app.db.session import get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.models.account_security import (  # noqa: E402
    EmailVerificationToken,
    PasswordResetToken,
    SecurityEvent,
)
from app.models.refresh_token import RefreshToken  # noqa: E402
from app.models.user import User, UserStatus  # noqa: E402
from app.services.email import clear_development_outbox, development_outbox  # noqa: E402
from app.services.rate_limit import reset_login_rate_limit_store  # noqa: E402


@pytest.fixture()
def client():
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

    clear_development_outbox()
    reset_login_rate_limit_store()
    asyncio.run(init_db())
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        test_client.testing_session = testing_session
        yield test_client

    app.dependency_overrides.clear()
    asyncio.run(dispose_db())


def signup(client: TestClient, email: str = "User@Example.com", password: str = "password123"):
    return client.post(
        "/api/v1/auth/signup",
        json={"name": "도하", "email": email, "password": password},
    )


def login(client: TestClient, email: str = "user@example.com", password: str = "password123"):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


async def set_user_status(testing_session, email: str, status: UserStatus) -> None:
    async with testing_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one()
        user.status = status
        await session.commit()


async def get_refresh_tokens(testing_session) -> list[RefreshToken]:
    async with testing_session() as session:
        result = await session.execute(select(RefreshToken))
        return list(result.scalars())


async def get_email_verification_tokens(testing_session) -> list[EmailVerificationToken]:
    async with testing_session() as session:
        result = await session.execute(select(EmailVerificationToken))
        return list(result.scalars())


async def get_password_reset_tokens(testing_session) -> list[PasswordResetToken]:
    async with testing_session() as session:
        result = await session.execute(select(PasswordResetToken))
        return list(result.scalars())


async def get_security_events(testing_session) -> list[SecurityEvent]:
    async with testing_session() as session:
        result = await session.execute(select(SecurityEvent))
        return list(result.scalars())


def token_from_last_email() -> str:
    body = development_outbox[-1].body
    for line in body.splitlines():
        if "token=" in line:
            return line.split("token=", 1)[1].strip()
    raise AssertionError("email token not found")


def test_signup_creates_user_without_password_hash_in_response(client):
    response = signup(client)

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "user@example.com"
    assert body["data"]["status"] == "ACTIVE"
    assert "password_hash" not in str(body)


def test_signup_rejects_duplicate_email(client):
    assert signup(client).status_code == 201

    response = signup(client, email=" user@example.com ")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "AUTH_EMAIL_ALREADY_EXISTS"


def test_signup_rejects_invalid_email(client):
    response = signup(client, email="not-an-email")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_signup_rejects_short_password(client):
    response = signup(client, password="short")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_login_issues_access_token_and_refresh_cookie(client):
    signup(client)
    response = login(client)

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["token_type"] == "Bearer"
    assert body["data"]["access_token"]
    assert REFRESH_TOKEN_COOKIE_NAME in response.cookies
    assert "password_hash" not in str(body).lower()
    assert "password123" not in str(body).lower()


def test_login_stores_refresh_token_hash(client):
    signup(client)
    response = login(client)
    refresh_token = response.cookies[REFRESH_TOKEN_COOKIE_NAME]

    tokens = asyncio.run(get_refresh_tokens(client.testing_session))

    assert len(tokens) == 1
    assert tokens[0].token_hash == hash_token(refresh_token)
    assert refresh_token not in tokens[0].token_hash


def test_login_rejects_wrong_password(client):
    signup(client)

    response = login(client, password="wrong-password")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_INVALID_CREDENTIALS"


def test_login_rejects_unknown_email(client):
    response = login(client, email="missing@example.com")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_INVALID_CREDENTIALS"


def test_login_rejects_inactive_user(client):
    signup(client)
    asyncio.run(set_user_status(client.testing_session, "user@example.com", UserStatus.INACTIVE))

    response = login(client)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AUTH_USER_INACTIVE"


def test_me_returns_current_user(client):
    signup(client)
    access_token = login(client).json()["data"]["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json()["data"]["email"] == "user@example.com"


def test_me_requires_token(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_TOKEN_MISSING"


def test_me_rejects_invalid_token(client):
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_TOKEN_INVALID"


def test_me_rejects_expired_access_token(client):
    signup(client)
    expired_token = create_jwt(1, "access", timedelta(seconds=-1))

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_TOKEN_EXPIRED"


def test_refresh_rotates_refresh_token(client):
    signup(client)
    old_refresh_token = login(client).cookies[REFRESH_TOKEN_COOKIE_NAME]

    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 200
    assert response.json()["data"]["access_token"]
    assert response.cookies[REFRESH_TOKEN_COOKIE_NAME] != old_refresh_token
    tokens = asyncio.run(get_refresh_tokens(client.testing_session))
    assert len(tokens) == 2
    assert sum(1 for token in tokens if token.revoked_at is not None) == 1


def test_refresh_rejects_reused_revoked_token(client):
    signup(client)
    old_refresh_token = login(client).cookies[REFRESH_TOKEN_COOKIE_NAME]
    assert client.post("/api/v1/auth/refresh").status_code == 200

    client.cookies.set(REFRESH_TOKEN_COOKIE_NAME, old_refresh_token, path="/api/v1/auth")
    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REFRESH_TOKEN_REVOKED"


def test_refresh_rejects_expired_refresh_token(client):
    expired_token = create_jwt(1, "refresh", timedelta(seconds=-1), "expired")
    client.cookies.set(REFRESH_TOKEN_COOKIE_NAME, expired_token, path="/api/v1/auth")

    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REFRESH_TOKEN_EXPIRED"


def test_refresh_rejects_invalid_refresh_token(client):
    client.cookies.set(REFRESH_TOKEN_COOKIE_NAME, "invalid", path="/api/v1/auth")

    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REFRESH_TOKEN_INVALID"


def test_logout_revokes_refresh_token_and_clears_cookie(client):
    signup(client)
    login(client)

    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    assert response.json()["data"] == {"logged_out": True}
    tokens = asyncio.run(get_refresh_tokens(client.testing_session))
    assert tokens[0].revoked_at is not None


def test_logout_is_idempotent(client):
    signup(client)
    login(client)

    assert client.post("/api/v1/auth/logout").status_code == 200
    assert client.post("/api/v1/auth/logout").status_code == 200


def test_logout_blocks_refresh_token_reuse(client):
    signup(client)
    refresh_token = login(client).cookies[REFRESH_TOKEN_COOKIE_NAME]
    client.post("/api/v1/auth/logout")
    client.cookies.set(REFRESH_TOKEN_COOKIE_NAME, refresh_token, path="/api/v1/auth")

    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REFRESH_TOKEN_REVOKED"


def test_access_token_is_issued(client):
    signup(client)
    response = login(client)

    assert response.json()["data"]["access_token"].count(".") == 2


def test_signup_creates_email_verification_token_and_sends_email(client):
    response = signup(client)

    tokens = asyncio.run(get_email_verification_tokens(client.testing_session))

    assert response.status_code == 201
    assert response.json()["data"]["email_verified"] is False
    assert response.json()["data"]["has_password"] is True
    assert len(tokens) == 1
    assert len(development_outbox) == 1
    assert "token=" in development_outbox[0].body
    assert tokens[0].token_hash not in development_outbox[0].body


def test_verify_email_marks_user_verified_and_consumes_token(client):
    signup(client)
    token = token_from_last_email()

    response = client.post("/api/v1/auth/email-verification/verify", json={"token": token})

    assert response.status_code == 200
    assert response.json()["data"]["email_verified"] is True
    tokens = asyncio.run(get_email_verification_tokens(client.testing_session))
    assert tokens[0].used_at is not None


def test_verify_email_rejects_reused_token(client):
    signup(client)
    token = token_from_last_email()
    assert (
        client.post("/api/v1/auth/email-verification/verify", json={"token": token}).status_code
        == 200
    )

    response = client.post("/api/v1/auth/email-verification/verify", json={"token": token})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "AUTH_EMAIL_VERIFICATION_TOKEN_INVALID"


def test_send_email_verification_requires_auth_and_rate_limits(client):
    signup(client)
    access_token = login(client).json()["data"]["access_token"]

    response = client.post(
        "/api/v1/auth/email-verification/send",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "AUTH_EMAIL_VERIFICATION_RESEND_LIMITED"


def test_forgot_password_returns_generic_response_and_sends_existing_user_email(client):
    signup(client)
    clear_development_outbox()

    response = client.post("/api/v1/auth/password/forgot", json={"email": "user@example.com"})
    missing_response = client.post(
        "/api/v1/auth/password/forgot", json={"email": "missing@example.com"}
    )

    assert response.status_code == 200
    assert missing_response.status_code == 200
    assert response.json()["data"] == missing_response.json()["data"]
    assert len(development_outbox) == 1
    assert len(asyncio.run(get_password_reset_tokens(client.testing_session))) == 1


def test_reset_password_revokes_sessions_and_rejects_token_reuse(client):
    signup(client)
    login(client)
    clear_development_outbox()
    client.post("/api/v1/auth/password/forgot", json={"email": "user@example.com"})
    reset_token = token_from_last_email()

    response = client.post(
        "/api/v1/auth/password/reset",
        json={
            "token": reset_token,
            "new_password": "new-password-123",
            "new_password_confirm": "new-password-123",
        },
    )
    reused_response = client.post(
        "/api/v1/auth/password/reset",
        json={
            "token": reset_token,
            "new_password": "new-password-456",
            "new_password_confirm": "new-password-456",
        },
    )

    assert response.status_code == 200
    assert reused_response.status_code == 400
    assert reused_response.json()["error"]["code"] == "AUTH_PASSWORD_RESET_TOKEN_INVALID"
    tokens = asyncio.run(get_refresh_tokens(client.testing_session))
    assert all(token.revoked_at is not None for token in tokens)
    assert login(client, password="new-password-123").status_code == 200


def test_password_change_revokes_other_sessions(client):
    signup(client)
    first_login = login(client)
    first_access = first_login.json()["data"]["access_token"]
    client.cookies.clear()
    assert login(client).status_code == 200
    second_refresh = client.cookies[REFRESH_TOKEN_COOKIE_NAME]
    client.cookies.set(
        REFRESH_TOKEN_COOKIE_NAME,
        first_login.cookies[REFRESH_TOKEN_COOKIE_NAME],
        path="/api/v1/auth",
    )

    response = client.post(
        "/api/v1/auth/password/change",
        headers={"Authorization": f"Bearer {first_access}"},
        json={
            "current_password": "password123",
            "new_password": "changed-password-123",
            "new_password_confirm": "changed-password-123",
        },
    )

    assert response.status_code == 200
    client.cookies.set(REFRESH_TOKEN_COOKIE_NAME, second_refresh, path="/api/v1/auth")
    rejected_refresh = client.post("/api/v1/auth/refresh")
    assert rejected_refresh.status_code == 401
    assert rejected_refresh.json()["error"]["code"] == "AUTH_REFRESH_TOKEN_REVOKED"


def test_sessions_can_be_listed_and_revoked(client):
    signup(client)
    first_login = login(client)
    access_token = first_login.json()["data"]["access_token"]
    client.cookies.clear()
    second_login = login(client)
    client.cookies.set(
        REFRESH_TOKEN_COOKIE_NAME,
        first_login.cookies[REFRESH_TOKEN_COOKIE_NAME],
        path="/api/v1/auth",
    )

    response = client.get(
        "/api/v1/auth/sessions",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    sessions = response.json()["data"]["sessions"]
    target = next(session for session in sessions if not session["current"])

    revoke_response = client.delete(
        f"/api/v1/auth/sessions/{target['session_id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert len(sessions) == 2
    assert revoke_response.status_code == 200
    client.cookies.set(
        REFRESH_TOKEN_COOKIE_NAME,
        second_login.cookies[REFRESH_TOKEN_COOKIE_NAME],
        path="/api/v1/auth",
    )
    assert client.post("/api/v1/auth/refresh").status_code == 401


def test_login_rate_limit_records_failures(client):
    signup(client)

    assert login(client, password="wrong-1").status_code == 401
    assert login(client, password="wrong-2").status_code == 401
    assert login(client, password="wrong-3").status_code == 401
    response = login(client, password="password123")

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "AUTH_LOGIN_RATE_LIMITED"


def test_security_events_do_not_store_secret_material(client):
    signup(client)
    login(client)
    events = asyncio.run(get_security_events(client.testing_session))

    assert events
    serialized = str([(event.event_type, event.event_metadata) for event in events])
    assert "password123" not in serialized
    assert "token=" not in serialized
