import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.security import (
    hash_ip_address,
    hash_password,
    hash_token,
    normalize_email,
    utc_now,
    validate_password,
    verify_password,
)
from app.models.account_security import SecurityEventType
from app.models.refresh_token import RefreshToken
from app.models.user import User, UserStatus
from app.repositories.account_security import AccountSecurityRepository
from app.repositories.auth import AuthRepository
from app.schemas.account_security import SessionPublic
from app.services.email import get_email_sender


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


class AccountSecurityService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = AccountSecurityRepository(session)
        self.auth_repository = AuthRepository(session)

    async def send_email_verification(
        self,
        user: User,
        user_agent: str | None = None,
        ip_address: str | None = None,
        commit: bool = True,
    ) -> None:
        if user.email_verified:
            raise AppError(
                "AUTH_EMAIL_ALREADY_VERIFIED",
                "이미 이메일 인증이 완료된 계정입니다.",
                409,
            )

        latest = await self.repository.latest_email_verification_token(user.id)
        if latest and latest.used_at is None:
            cooldown_until = _aware(latest.created_at) + timedelta(
                seconds=settings.email_resend_cooldown_seconds
            )
            if cooldown_until > utc_now():
                raise AppError(
                    "AUTH_EMAIL_VERIFICATION_RESEND_LIMITED",
                    "이메일 인증 요청이 너무 잦습니다. 잠시 후 다시 시도해 주세요.",
                    429,
                )

        await self.repository.mark_unused_email_tokens_used(user.id)
        raw_token = secrets.token_urlsafe(32)
        expires_at = utc_now() + timedelta(minutes=settings.email_verification_expire_minutes)
        await self.repository.create_email_verification_token(
            user.id,
            hash_token(raw_token),
            expires_at,
        )
        verify_url = f"{settings.frontend_email_verify_url}?{urlencode({'token': raw_token})}"
        await get_email_sender().send(
            to=user.email,
            subject="[ApplyMate AI] 이메일 인증을 완료해 주세요",
            body=(
                "ApplyMate AI 이메일 인증 링크입니다.\n\n"
                f"{verify_url}\n\n"
                f"이 링크는 {settings.email_verification_expire_minutes}분 동안 유효합니다."
            ),
        )
        await self.repository.create_security_event(
            SecurityEventType.EMAIL_VERIFICATION_SENT,
            user_id=user.id,
            ip_address_hash=hash_ip_address(ip_address),
            user_agent=user_agent,
        )
        if commit:
            await self.session.commit()

    async def verify_email(
        self, token: str, user_agent: str | None, ip_address: str | None
    ) -> User:
        stored = await self.repository.get_email_verification_token(hash_token(token))
        if not stored or stored.used_at is not None:
            raise AppError(
                "AUTH_EMAIL_VERIFICATION_TOKEN_INVALID",
                "유효하지 않은 이메일 인증 토큰입니다.",
                400,
            )
        if _aware(stored.expires_at) < utc_now():
            raise AppError(
                "AUTH_EMAIL_VERIFICATION_TOKEN_EXPIRED",
                "이메일 인증 토큰이 만료되었습니다.",
                400,
            )
        user = await self.auth_repository.get_user_by_id(stored.user_id)
        if not user or user.status != UserStatus.ACTIVE:
            raise AppError("AUTH_USER_INACTIVE", "비활성 사용자입니다.", 403)

        user.email_verified = True
        stored.used_at = utc_now()
        await self.repository.mark_unused_email_tokens_used(user.id)
        await self.repository.create_security_event(
            SecurityEventType.EMAIL_VERIFIED,
            user_id=user.id,
            ip_address_hash=hash_ip_address(ip_address),
            user_agent=user_agent,
        )
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def request_password_reset(
        self, email: str, user_agent: str | None, ip_address: str | None
    ) -> None:
        normalized_email = normalize_email(email)
        user = await self.auth_repository.get_user_by_email(normalized_email)
        if not user or user.status != UserStatus.ACTIVE:
            return

        await self.repository.mark_unused_password_reset_tokens_used(user.id)
        raw_token = secrets.token_urlsafe(32)
        expires_at = utc_now() + timedelta(minutes=settings.password_reset_expire_minutes)
        await self.repository.create_password_reset_token(
            user.id, hash_token(raw_token), expires_at
        )
        reset_url = f"{settings.frontend_password_reset_url}?{urlencode({'token': raw_token})}"
        await get_email_sender().send(
            to=user.email,
            subject="[ApplyMate AI] 비밀번호 재설정 안내",
            body=(
                "ApplyMate AI 비밀번호 재설정 링크입니다.\n\n"
                f"{reset_url}\n\n"
                f"이 링크는 {settings.password_reset_expire_minutes}분 동안 유효합니다."
            ),
        )
        await self.repository.create_security_event(
            SecurityEventType.PASSWORD_RESET_REQUESTED,
            user_id=user.id,
            ip_address_hash=hash_ip_address(ip_address),
            user_agent=user_agent,
        )
        await self.session.commit()

    async def reset_password(
        self,
        token: str,
        new_password: str,
        new_password_confirm: str,
        user_agent: str | None,
        ip_address: str | None,
    ) -> User:
        if new_password != new_password_confirm:
            raise AppError("VALIDATION_ERROR", "새 비밀번호 확인이 일치하지 않습니다.", 422)

        stored = await self.repository.get_password_reset_token(hash_token(token))
        if not stored or stored.used_at is not None:
            raise AppError(
                "AUTH_PASSWORD_RESET_TOKEN_INVALID",
                "유효하지 않은 비밀번호 재설정 토큰입니다.",
                400,
            )
        if _aware(stored.expires_at) < utc_now():
            raise AppError(
                "AUTH_PASSWORD_RESET_TOKEN_EXPIRED",
                "비밀번호 재설정 토큰이 만료되었습니다.",
                400,
            )
        user = await self.auth_repository.get_user_by_id(stored.user_id)
        if not user or user.status != UserStatus.ACTIVE:
            raise AppError("AUTH_USER_INACTIVE", "비활성 사용자입니다.", 403)

        validate_password(new_password, user.email)
        if user.password_hash and verify_password(new_password, user.password_hash):
            raise AppError(
                "AUTH_PASSWORD_REUSE_NOT_ALLOWED",
                "기존 비밀번호와 같은 비밀번호는 사용할 수 없습니다.",
                400,
            )

        user.password_hash = hash_password(new_password)
        stored.used_at = utc_now()
        await self.repository.mark_unused_password_reset_tokens_used(user.id)
        await self.auth_repository.revoke_all_sessions(user.id)
        await self.repository.create_security_event(
            SecurityEventType.PASSWORD_RESET_COMPLETED,
            user_id=user.id,
            ip_address_hash=hash_ip_address(ip_address),
            user_agent=user_agent,
        )
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
        new_password_confirm: str,
        refresh_token: str | None,
        user_agent: str | None,
        ip_address: str | None,
    ) -> int:
        if not user.password_hash:
            raise AppError(
                "AUTH_PASSWORD_NOT_CONFIGURED",
                "비밀번호가 설정되지 않은 계정입니다.",
                400,
            )
        if not verify_password(current_password, user.password_hash):
            raise AppError(
                "AUTH_INVALID_CURRENT_PASSWORD",
                "현재 비밀번호가 올바르지 않습니다.",
                401,
            )
        if new_password != new_password_confirm:
            raise AppError("VALIDATION_ERROR", "새 비밀번호 확인이 일치하지 않습니다.", 422)
        validate_password(new_password, user.email)
        if verify_password(new_password, user.password_hash):
            raise AppError(
                "AUTH_PASSWORD_REUSE_NOT_ALLOWED",
                "기존 비밀번호와 같은 비밀번호는 사용할 수 없습니다.",
                400,
            )

        user.password_hash = hash_password(new_password)
        current_session_id = await self.current_session_id(user.id, refresh_token)
        revoked_count = (
            await self.auth_repository.revoke_other_sessions(user.id, current_session_id)
            if current_session_id
            else await self.auth_repository.revoke_all_sessions(user.id)
        )
        await self.repository.create_security_event(
            SecurityEventType.PASSWORD_CHANGED,
            user_id=user.id,
            session_id=current_session_id,
            ip_address_hash=hash_ip_address(ip_address),
            user_agent=user_agent,
        )
        await self.session.commit()
        return revoked_count

    async def set_password(
        self,
        user: User,
        new_password: str,
        new_password_confirm: str,
        user_agent: str | None,
        ip_address: str | None,
    ) -> None:
        if user.password_hash:
            raise AppError(
                "AUTH_PASSWORD_ALREADY_CONFIGURED",
                "이미 비밀번호가 설정된 계정입니다.",
                409,
            )
        if not user.email_verified:
            raise AppError(
                "AUTH_EMAIL_VERIFICATION_REQUIRED",
                "비밀번호 설정 전 이메일 인증이 필요합니다.",
                403,
            )
        if new_password != new_password_confirm:
            raise AppError("VALIDATION_ERROR", "새 비밀번호 확인이 일치하지 않습니다.", 422)
        validate_password(new_password, user.email)
        user.password_hash = hash_password(new_password)
        await self.repository.create_security_event(
            SecurityEventType.PASSWORD_CONFIGURED,
            user_id=user.id,
            ip_address_hash=hash_ip_address(ip_address),
            user_agent=user_agent,
        )
        await self.session.commit()

    async def list_sessions(self, user: User, refresh_token: str | None) -> list[SessionPublic]:
        active_tokens = await self.auth_repository.list_active_refresh_tokens(user.id)
        current_session_id = await self.current_session_id(user.id, refresh_token)
        return [
            self.to_session_public(token, current_session_id)
            for token in self.latest_token_per_session(active_tokens)
        ]

    def latest_token_per_session(self, tokens: list[RefreshToken]) -> list[RefreshToken]:
        sessions: dict[str, RefreshToken] = {}
        for token in tokens:
            existing = sessions.get(token.session_id)
            if not existing or _aware(token.created_at) > _aware(existing.created_at):
                sessions[token.session_id] = token
        return sorted(
            sessions.values(),
            key=lambda token: _aware(token.last_used_at or token.created_at),
            reverse=True,
        )

    def to_session_public(
        self, token: RefreshToken, current_session_id: str | None
    ) -> SessionPublic:
        return SessionPublic(
            session_id=token.session_id,
            device_name=token.device_name,
            device_info=token.device_info,
            user_agent=token.user_agent,
            current=token.session_id == current_session_id,
            created_at=token.created_at,
            last_used_at=token.last_used_at,
            expires_at=token.expires_at,
        )

    async def current_session_id(self, user_id: int, refresh_token: str | None) -> str | None:
        if not refresh_token:
            return None
        stored = await self.auth_repository.get_refresh_token(hash_token(refresh_token))
        if not stored or stored.user_id != user_id or stored.revoked_at is not None:
            return None
        return stored.session_id

    async def revoke_session(
        self,
        user: User,
        session_id: str,
        refresh_token: str | None,
        user_agent: str | None,
        ip_address: str | None,
    ) -> int:
        current_session_id = await self.current_session_id(user.id, refresh_token)
        if current_session_id == session_id:
            raise AppError(
                "AUTH_SESSION_CURRENT_REVOKE_NOT_ALLOWED",
                "현재 사용 중인 세션은 이 API에서 해제할 수 없습니다.",
                400,
            )
        active = await self.auth_repository.get_active_session(user.id, session_id)
        if not active:
            raise AppError("AUTH_SESSION_NOT_FOUND", "세션을 찾을 수 없습니다.", 404)
        revoked_count = await self.auth_repository.revoke_session(user.id, session_id)
        await self.repository.create_security_event(
            SecurityEventType.SESSION_REVOKED,
            user_id=user.id,
            session_id=session_id,
            ip_address_hash=hash_ip_address(ip_address),
            user_agent=user_agent,
        )
        await self.session.commit()
        return revoked_count

    async def revoke_other_sessions(
        self,
        user: User,
        refresh_token: str | None,
        user_agent: str | None,
        ip_address: str | None,
    ) -> int:
        current_session_id = await self.current_session_id(user.id, refresh_token)
        if not current_session_id:
            raise AppError("AUTH_SESSION_NOT_FOUND", "현재 세션을 찾을 수 없습니다.", 404)
        revoked_count = await self.auth_repository.revoke_other_sessions(
            user.id, current_session_id
        )
        await self.repository.create_security_event(
            SecurityEventType.SESSION_REVOKED,
            user_id=user.id,
            session_id=current_session_id,
            ip_address_hash=hash_ip_address(ip_address),
            user_agent=user_agent,
            event_metadata={"scope": "others"},
        )
        await self.session.commit()
        return revoked_count

    async def revoke_all_sessions(
        self, user: User, user_agent: str | None, ip_address: str | None
    ) -> int:
        revoked_count = await self.auth_repository.revoke_all_sessions(user.id)
        await self.repository.create_security_event(
            SecurityEventType.LOGOUT_ALL,
            user_id=user.id,
            ip_address_hash=hash_ip_address(ip_address),
            user_agent=user_agent,
        )
        await self.session.commit()
        return revoked_count

    async def list_security_events(self, user: User, limit: int = 20):
        return await self.repository.list_security_events(user.id, limit)
