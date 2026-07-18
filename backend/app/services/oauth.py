from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urlencode
import secrets

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.security import hash_token, normalize_email, utc_now, validate_email
from app.models.oauth import OAuthAccount, OAuthProvider, OAuthPurpose
from app.models.user import User, UserStatus
from app.repositories.auth import AuthRepository
from app.repositories.oauth import OAuthRepository
from app.services.auth import AuthService


@dataclass(frozen=True)
class OAuthProviderConfig:
    provider: OAuthProvider
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str

    @property
    def enabled(self) -> bool:
        return bool(self.client_id and self.client_secret and self.redirect_uri)


@dataclass(frozen=True)
class OAuthUserInfo:
    provider: OAuthProvider
    provider_user_id: str
    email: str | None
    email_verified: bool
    username: str | None
    display_name: str | None


class OAuthProviderAdapter:
    authorization_endpoint: str
    token_endpoint: str

    def __init__(self, config: OAuthProviderConfig) -> None:
        self.config = config

    def authorization_url(self, state: str) -> str:
        raise NotImplementedError

    async def fetch_user_info(self, code: str) -> OAuthUserInfo:
        raise NotImplementedError


class GoogleOAuthAdapter(OAuthProviderAdapter):
    authorization_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
    token_endpoint = "https://oauth2.googleapis.com/token"
    userinfo_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"

    def authorization_url(self, state: str) -> str:
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "scope": self.config.scope,
            "state": state,
            "prompt": "select_account",
        }
        return f"{self.authorization_endpoint}?{urlencode(params)}"

    async def fetch_user_info(self, code: str) -> OAuthUserInfo:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                token_response = await client.post(
                    self.token_endpoint,
                    data={
                        "client_id": self.config.client_id,
                        "client_secret": self.config.client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": self.config.redirect_uri,
                    },
                )
                token_response.raise_for_status()
                access_token = token_response.json().get("access_token")
                if not access_token:
                    raise AppError(
                        "OAUTH_CODE_EXCHANGE_FAILED",
                        "OAuth code 교환에 실패했습니다.",
                        400,
                    )

                user_response = await client.get(
                    self.userinfo_endpoint,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                user_response.raise_for_status()
                data = user_response.json()
        except AppError:
            raise
        except httpx.HTTPStatusError as exc:
            raise AppError(
                "OAUTH_PROVIDER_REQUEST_FAILED",
                "OAuth provider 요청에 실패했습니다.",
                400,
            ) from exc
        except httpx.HTTPError as exc:
            raise AppError(
                "OAUTH_PROVIDER_REQUEST_FAILED",
                "OAuth provider에 연결할 수 없습니다.",
                400,
            ) from exc

        provider_user_id = str(data.get("sub") or "")
        if not provider_user_id:
            raise AppError(
                "OAUTH_PROVIDER_USER_INVALID",
                "OAuth 사용자 정보를 확인할 수 없습니다.",
                400,
            )

        return OAuthUserInfo(
            provider=OAuthProvider.GOOGLE,
            provider_user_id=provider_user_id,
            email=data.get("email"),
            email_verified=bool(data.get("email_verified")),
            username=data.get("email"),
            display_name=data.get("name"),
        )


class GitHubOAuthAdapter(OAuthProviderAdapter):
    authorization_endpoint = "https://github.com/login/oauth/authorize"
    token_endpoint = "https://github.com/login/oauth/access_token"
    user_endpoint = "https://api.github.com/user"
    emails_endpoint = "https://api.github.com/user/emails"

    def authorization_url(self, state: str) -> str:
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": self.config.scope,
            "state": state,
        }
        return f"{self.authorization_endpoint}?{urlencode(params)}"

    async def fetch_user_info(self, code: str) -> OAuthUserInfo:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                token_response = await client.post(
                    self.token_endpoint,
                    data={
                        "client_id": self.config.client_id,
                        "client_secret": self.config.client_secret,
                        "code": code,
                        "redirect_uri": self.config.redirect_uri,
                    },
                    headers={"Accept": "application/json"},
                )
                token_response.raise_for_status()
                access_token = token_response.json().get("access_token")
                if not access_token:
                    raise AppError(
                        "OAUTH_CODE_EXCHANGE_FAILED",
                        "OAuth code 교환에 실패했습니다.",
                        400,
                    )

                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                }
                user_response = await client.get(self.user_endpoint, headers=headers)
                user_response.raise_for_status()
                user_data = user_response.json()

                email = user_data.get("email")
                email_verified = bool(email)
                if not email:
                    emails_response = await client.get(self.emails_endpoint, headers=headers)
                    emails_response.raise_for_status()
                    email, email_verified = self.pick_verified_email(emails_response.json())
        except AppError:
            raise
        except httpx.HTTPStatusError as exc:
            raise AppError(
                "OAUTH_PROVIDER_REQUEST_FAILED",
                "OAuth provider 요청에 실패했습니다.",
                400,
            ) from exc
        except httpx.HTTPError as exc:
            raise AppError(
                "OAUTH_PROVIDER_REQUEST_FAILED",
                "OAuth provider에 연결할 수 없습니다.",
                400,
            ) from exc

        provider_user_id = str(user_data.get("id") or "")
        if not provider_user_id:
            raise AppError(
                "OAUTH_PROVIDER_USER_INVALID",
                "OAuth 사용자 정보를 확인할 수 없습니다.",
                400,
            )

        return OAuthUserInfo(
            provider=OAuthProvider.GITHUB,
            provider_user_id=provider_user_id,
            email=email,
            email_verified=email_verified,
            username=user_data.get("login"),
            display_name=user_data.get("name") or user_data.get("login"),
        )

    def pick_verified_email(self, emails: list[dict[str, object]]) -> tuple[str | None, bool]:
        verified = [item for item in emails if item.get("verified") and item.get("email")]
        primary = [item for item in verified if item.get("primary")]
        selected = (primary or verified)[0] if verified else None
        if not selected:
            return None, False
        return str(selected["email"]), True


def provider_from_path(value: str) -> OAuthProvider:
    normalized = value.strip().upper()
    try:
        return OAuthProvider(normalized)
    except ValueError as exc:
        raise AppError(
            "OAUTH_PROVIDER_NOT_SUPPORTED",
            "지원하지 않는 OAuth provider입니다.",
            404,
        ) from exc


class OAuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = OAuthRepository(session)
        self.auth_repository = AuthRepository(session)

    def provider_config(self, provider: OAuthProvider) -> OAuthProviderConfig:
        if provider == OAuthProvider.GOOGLE:
            return OAuthProviderConfig(
                provider=provider,
                client_id=settings.google_client_id,
                client_secret=settings.google_client_secret,
                redirect_uri=settings.google_redirect_uri,
                scope="openid email profile",
            )
        return OAuthProviderConfig(
            provider=provider,
            client_id=settings.github_client_id,
            client_secret=settings.github_client_secret,
            redirect_uri=settings.github_redirect_uri,
            scope="read:user user:email",
        )

    def get_adapter(self, provider: OAuthProvider) -> OAuthProviderAdapter:
        config = self.provider_config(provider)
        if not config.enabled:
            raise AppError(
                "OAUTH_PROVIDER_DISABLED",
                "OAuth provider가 설정되어 있지 않습니다.",
                400,
            )
        if provider == OAuthProvider.GOOGLE:
            return GoogleOAuthAdapter(config)
        if provider == OAuthProvider.GITHUB:
            return GitHubOAuthAdapter(config)
        raise AppError("OAUTH_PROVIDER_NOT_SUPPORTED", "지원하지 않는 OAuth provider입니다.", 404)

    def providers(self) -> list[dict[str, OAuthProvider | bool]]:
        return [
            {"provider": provider, "enabled": self.provider_config(provider).enabled}
            for provider in OAuthProvider
        ]

    def normalize_redirect_path(self, redirect_path: str | None) -> str:
        path = redirect_path or "/me"
        if not path.startswith("/") or path.startswith("//"):
            raise AppError("OAUTH_REDIRECT_NOT_ALLOWED", "허용되지 않은 redirect_path입니다.", 400)
        if path not in settings.oauth_allowed_redirect_paths:
            raise AppError("OAUTH_REDIRECT_NOT_ALLOWED", "허용되지 않은 redirect_path입니다.", 400)
        return path

    async def create_authorization_url(
        self,
        provider: OAuthProvider,
        purpose: OAuthPurpose,
        redirect_path: str | None,
        user_id: int | None = None,
    ) -> str:
        if purpose == OAuthPurpose.LINK and user_id is None:
            raise AppError("AUTH_UNAUTHORIZED", "인증이 필요합니다.", 401)

        normalized_redirect_path = self.normalize_redirect_path(redirect_path)
        adapter = self.get_adapter(provider)
        raw_state = secrets.token_urlsafe(32)
        expires_at = utc_now() + timedelta(seconds=settings.oauth_state_expire_seconds)
        await self.repository.create_state(
            state_hash=hash_token(raw_state),
            provider=provider,
            purpose=purpose,
            user_id=user_id,
            redirect_path=normalized_redirect_path,
            expires_at=expires_at,
        )
        await self.session.commit()
        return adapter.authorization_url(raw_state)

    async def handle_callback(
        self,
        provider: OAuthProvider,
        code: str | None,
        state: str | None,
        provider_error: str | None,
    ) -> tuple[str | None, str | None, str]:
        if provider_error:
            return None, "OAUTH_PROVIDER_REQUEST_FAILED", "/login"
        if not code:
            return None, "OAUTH_CODE_MISSING", "/login"
        oauth_state = await self.consume_state(provider, state)
        user_info = await self.get_adapter(provider).fetch_user_info(code)

        if oauth_state.purpose == OAuthPurpose.LINK:
            await self.link_account(oauth_state.user_id, user_info)
            await self.session.commit()
            return None, None, "/settings/accounts"

        user = await self.resolve_login_user(user_info)
        ticket = await self.create_login_ticket(user.id, provider, oauth_state.redirect_path)
        await self.session.commit()
        return ticket, None, oauth_state.redirect_path

    async def consume_state(self, provider: OAuthProvider, state: str | None):
        if not state:
            raise AppError("OAUTH_STATE_MISSING", "OAuth state가 필요합니다.", 400)
        oauth_state = await self.repository.get_state(hash_token(state))
        if not oauth_state or oauth_state.consumed_at is not None:
            raise AppError("OAUTH_STATE_INVALID", "유효하지 않은 OAuth state입니다.", 400)
        if oauth_state.provider != provider:
            raise AppError(
                "OAUTH_STATE_INVALID",
                "OAuth state provider가 일치하지 않습니다.",
                400,
            )
        if oauth_state.expires_at.replace(tzinfo=utc_now().tzinfo) < utc_now():
            raise AppError("OAUTH_STATE_EXPIRED", "OAuth state가 만료되었습니다.", 400)
        oauth_state.consumed_at = utc_now()
        return oauth_state

    async def resolve_login_user(self, user_info: OAuthUserInfo) -> User:
        self.ensure_verified_email(user_info)
        account = await self.repository.get_account_by_provider_user(
            user_info.provider, user_info.provider_user_id
        )
        if account:
            user = await self.auth_repository.get_user_by_id(account.user_id)
            if not user or user.status != UserStatus.ACTIVE:
                raise AppError("AUTH_USER_INACTIVE", "비활성 사용자입니다.", 403)
            account.last_login_at = utc_now()
            return user

        assert user_info.email is not None
        normalized_email = validate_email(user_info.email)
        existing_user = await self.auth_repository.get_user_by_email(normalized_email)
        if existing_user:
            raise AppError(
                "OAUTH_ACCOUNT_LINK_REQUIRED",
                "같은 이메일의 기존 계정이 있습니다. 로그인 후 계정 연결 화면에서 소셜 계정을 연결해 주세요.",
                409,
            )

        user = await self.auth_repository.create_user(
            email=normalized_email,
            password_hash=None,
            name=(user_info.display_name or user_info.username or normalized_email).strip(),
            email_verified=True,
        )
        account = await self.repository.create_account(
            user_id=user.id,
            provider=user_info.provider,
            provider_user_id=user_info.provider_user_id,
            provider_email=normalize_email(user_info.email),
            provider_username=user_info.username,
            provider_display_name=user_info.display_name,
            email_verified=user_info.email_verified,
        )
        account.last_login_at = utc_now()
        return user

    async def link_account(self, user_id: int | None, user_info: OAuthUserInfo) -> OAuthAccount:
        if user_id is None:
            raise AppError("AUTH_UNAUTHORIZED", "인증이 필요합니다.", 401)
        self.ensure_verified_email(user_info)
        linked = await self.repository.get_account_by_provider_user(
            user_info.provider, user_info.provider_user_id
        )
        if linked and linked.user_id != user_id:
            raise AppError(
                "OAUTH_ACCOUNT_LINKED_TO_OTHER_USER",
                "이미 다른 사용자에게 연결된 소셜 계정입니다.",
                409,
            )
        existing = await self.repository.get_user_provider_account(user_id, user_info.provider)
        if existing:
            raise AppError("OAUTH_ACCOUNT_ALREADY_LINKED", "이미 연결된 provider입니다.", 409)

        assert user_info.email is not None
        return await self.repository.create_account(
            user_id=user_id,
            provider=user_info.provider,
            provider_user_id=user_info.provider_user_id,
            provider_email=normalize_email(user_info.email),
            provider_username=user_info.username,
            provider_display_name=user_info.display_name,
            email_verified=user_info.email_verified,
        )

    def ensure_verified_email(self, user_info: OAuthUserInfo) -> None:
        if not user_info.email or not user_info.email_verified:
            raise AppError(
                "OAUTH_VERIFIED_EMAIL_REQUIRED",
                "검증된 이메일을 제공하는 소셜 계정만 사용할 수 있습니다.",
                400,
            )

    async def create_login_ticket(
        self, user_id: int, provider: OAuthProvider, redirect_path: str
    ) -> str:
        raw_ticket = secrets.token_urlsafe(32)
        await self.repository.create_ticket(
            ticket_hash=hash_token(raw_ticket),
            user_id=user_id,
            provider=provider,
            redirect_path=redirect_path,
            expires_at=utc_now() + timedelta(seconds=settings.oauth_ticket_expire_seconds),
        )
        return raw_ticket

    async def exchange_ticket(
        self, ticket: str, device_info: str | None
    ) -> tuple[User, str, str, datetime, str, OAuthProvider]:
        stored = await self.repository.get_ticket(hash_token(ticket))
        if not stored or stored.consumed_at is not None:
            raise AppError("OAUTH_TICKET_INVALID", "유효하지 않은 OAuth ticket입니다.", 401)
        if stored.expires_at.replace(tzinfo=utc_now().tzinfo) < utc_now():
            raise AppError("OAUTH_TICKET_EXPIRED", "OAuth ticket이 만료되었습니다.", 401)
        user = await self.auth_repository.get_user_by_id(stored.user_id)
        if not user or user.status != UserStatus.ACTIVE:
            raise AppError("AUTH_USER_INACTIVE", "비활성 사용자입니다.", 403)
        stored.consumed_at = utc_now()
        user, access_token, refresh_token, refresh_expires_at = await AuthService(
            self.session
        ).issue_tokens(user, device_info)
        return (
            user,
            access_token,
            refresh_token,
            refresh_expires_at,
            stored.redirect_path,
            stored.provider,
        )

    async def list_accounts(self, user: User) -> list[dict[str, object]]:
        accounts = await self.repository.list_accounts(user.id)
        can_unlink = user.password_hash is not None or len(accounts) > 1
        return [
            {
                "provider": account.provider,
                "provider_email": account.provider_email,
                "provider_username": account.provider_username,
                "provider_display_name": account.provider_display_name,
                "email_verified": account.email_verified,
                "created_at": account.created_at,
                "last_login_at": account.last_login_at,
                "can_unlink": can_unlink,
            }
            for account in accounts
        ]

    async def unlink_account(self, user: User, provider: OAuthProvider) -> None:
        account = await self.repository.get_user_provider_account(user.id, provider)
        if not account:
            raise AppError("OAUTH_ACCOUNT_NOT_FOUND", "연결된 소셜 계정을 찾을 수 없습니다.", 404)
        account_count = await self.repository.count_accounts(user.id)
        if user.password_hash is None and account_count <= 1:
            raise AppError(
                "OAUTH_LAST_LOGIN_METHOD",
                "마지막 로그인 수단은 해제할 수 없습니다.",
                400,
            )
        await self.session.delete(account)
        await self.session.commit()


def frontend_callback_url(ticket: str | None, error: str | None, redirect_path: str) -> str:
    params: dict[str, str] = {"redirect_path": redirect_path}
    if ticket:
        params["ticket"] = ticket
    if error:
        params["error"] = error
    return f"{settings.oauth_frontend_callback_url}?{urlencode(params)}"
