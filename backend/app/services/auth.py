import secrets
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_jwt,
    hash_ip_address,
    hash_password,
    hash_token,
    normalize_email,
    utc_now,
    validate_email,
    validate_password,
    verify_password,
)
from app.models.account_security import SecurityEventType
from app.models.user import User, UserStatus
from app.repositories.account_security import AccountSecurityRepository
from app.repositories.auth import AuthRepository
from app.services.account_security import AccountSecurityService
from app.services.rate_limit import LoginRateLimiter


def _device_name_from_user_agent(user_agent: str | None) -> str | None:
    if not user_agent:
        return None
    lowered = user_agent.lower()
    if "iphone" in lowered:
        return "iPhone"
    if "android" in lowered:
        return "Android"
    if "windows" in lowered:
        return "Windows"
    if "mac os" in lowered or "macintosh" in lowered:
        return "Mac"
    if "linux" in lowered:
        return "Linux"
    return "Unknown device"


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = AuthRepository(session)
        self.security_repository = AccountSecurityRepository(session)
        self.rate_limiter = LoginRateLimiter()

    async def signup(
        self,
        email: str,
        password: str,
        name: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> User:
        normalized_email = validate_email(email)
        validate_password(password, normalized_email)

        existing = await self.repository.get_user_by_email(normalized_email)
        if existing:
            raise AppError("AUTH_EMAIL_ALREADY_EXISTS", "이미 가입된 이메일입니다.", 409)

        user = await self.repository.create_user(
            normalized_email, hash_password(password), name.strip(), email_verified=False
        )
        await AccountSecurityService(self.session).send_email_verification(
            user,
            user_agent=user_agent,
            ip_address=ip_address,
            commit=False,
        )
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def login(
        self, email: str, password: str, device_info: str | None, ip_address: str | None = None
    ) -> tuple[User, str, str, datetime]:
        normalized_email = normalize_email(email)
        self.rate_limiter.check(normalized_email)

        user = await self.repository.get_user_by_email(normalized_email)
        if not user or user.password_hash is None:
            await self.record_failed_login(normalized_email, user, device_info, ip_address)
            raise AppError(
                "AUTH_INVALID_CREDENTIALS",
                "이메일 또는 비밀번호가 올바르지 않습니다.",
                401,
            )
        if not verify_password(password, user.password_hash):
            await self.record_failed_login(normalized_email, user, device_info, ip_address)
            raise AppError(
                "AUTH_INVALID_CREDENTIALS",
                "이메일 또는 비밀번호가 올바르지 않습니다.",
                401,
            )
        if user.status != UserStatus.ACTIVE:
            raise AppError("AUTH_USER_INACTIVE", "비활성 사용자입니다.", 403)

        self.rate_limiter.reset(normalized_email)
        return await self.issue_tokens(user, device_info, ip_address)

    async def record_failed_login(
        self,
        normalized_email: str,
        user: User | None,
        user_agent: str | None,
        ip_address: str | None,
    ) -> None:
        self.rate_limiter.record_failure(normalized_email)
        await self.security_repository.create_security_event(
            SecurityEventType.LOGIN_FAILED,
            user_id=user.id if user else None,
            ip_address_hash=hash_ip_address(ip_address),
            user_agent=user_agent,
        )
        await self.session.commit()

    async def issue_tokens(
        self,
        user: User,
        device_info: str | None,
        ip_address: str | None = None,
        session_id: str | None = None,
        device_name: str | None = None,
    ) -> tuple[User, str, str, datetime]:
        current_session_id = session_id or secrets.token_urlsafe(24)
        access_token = create_access_token(user.id)
        refresh_token, _jti, refresh_expires_at = create_refresh_token(user.id)
        await self.repository.save_refresh_token(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=refresh_expires_at,
            session_id=current_session_id,
            device_info=device_info,
            device_name=device_name or _device_name_from_user_agent(device_info),
            user_agent=device_info,
            ip_address_hash=hash_ip_address(ip_address),
            last_used_at=utc_now(),
        )
        user.last_login_at = utc_now()
        await self.security_repository.create_security_event(
            SecurityEventType.LOGIN_SUCCESS,
            user_id=user.id,
            session_id=current_session_id,
            ip_address_hash=hash_ip_address(ip_address),
            user_agent=device_info,
        )
        await self.session.commit()
        await self.session.refresh(user)
        return user, access_token, refresh_token, refresh_expires_at

    async def refresh(
        self,
        refresh_token: str | None,
        device_info: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[User, str, str, datetime]:
        if not refresh_token:
            raise AppError("AUTH_REFRESH_TOKEN_INVALID", "Refresh Token이 필요합니다.", 401)

        payload = decode_jwt(refresh_token, "refresh")
        stored_token = await self.repository.get_refresh_token(hash_token(refresh_token))
        if not stored_token:
            raise AppError("AUTH_REFRESH_TOKEN_INVALID", "유효하지 않은 Refresh Token입니다.", 401)
        if stored_token.revoked_at is not None:
            raise AppError("AUTH_REFRESH_TOKEN_REVOKED", "폐기된 Refresh Token입니다.", 401)
        if stored_token.expires_at.replace(tzinfo=UTC) < utc_now():
            raise AppError("AUTH_REFRESH_TOKEN_EXPIRED", "Refresh Token이 만료되었습니다.", 401)

        user = await self.repository.get_user_by_id(int(payload["sub"]))
        if not user or user.id != stored_token.user_id:
            raise AppError("AUTH_REFRESH_TOKEN_INVALID", "유효하지 않은 Refresh Token입니다.", 401)
        if user.status != UserStatus.ACTIVE:
            raise AppError("AUTH_USER_INACTIVE", "비활성 사용자입니다.", 403)

        stored_token.revoked_at = utc_now()
        return await self.issue_tokens(
            user,
            device_info or stored_token.device_info,
            ip_address,
            session_id=stored_token.session_id,
            device_name=stored_token.device_name,
        )

    async def logout(self, refresh_token: str | None, user_agent: str | None = None) -> None:
        if refresh_token:
            stored_token = await self.repository.get_refresh_token(hash_token(refresh_token))
            if stored_token and stored_token.revoked_at is None:
                stored_token.revoked_at = utc_now()
                await self.security_repository.create_security_event(
                    SecurityEventType.LOGOUT,
                    user_id=stored_token.user_id,
                    session_id=stored_token.session_id,
                    user_agent=user_agent,
                )
                await self.session.commit()

    async def get_active_user(self, user_id: int) -> User:
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise AppError("AUTH_UNAUTHORIZED", "인증이 필요합니다.", 401)
        if user.status != UserStatus.ACTIVE:
            raise AppError("AUTH_USER_INACTIVE", "비활성 사용자입니다.", 403)
        return user
