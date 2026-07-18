from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_jwt,
    hash_password,
    hash_token,
    normalize_email,
    utc_now,
    validate_email,
    validate_password,
    verify_password,
)
from app.models.user import User, UserStatus
from app.repositories.auth import AuthRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = AuthRepository(session)

    async def signup(self, email: str, password: str, name: str) -> User:
        normalized_email = validate_email(email)
        validate_password(password)

        existing = await self.repository.get_user_by_email(normalized_email)
        if existing:
            raise AppError("AUTH_EMAIL_ALREADY_EXISTS", "이미 가입된 이메일입니다.", 409)

        user = await self.repository.create_user(
            normalized_email, hash_password(password), name.strip()
        )
        await self.session.commit()
        return user

    async def login(
        self, email: str, password: str, device_info: str | None
    ) -> tuple[User, str, str, datetime]:
        user = await self.repository.get_user_by_email(normalize_email(email))
        if not user or not verify_password(password, user.password_hash):
            raise AppError("AUTH_INVALID_CREDENTIALS", "이메일 또는 비밀번호가 올바르지 않습니다.", 401)
        if user.status != UserStatus.ACTIVE:
            raise AppError("AUTH_USER_INACTIVE", "비활성 사용자입니다.", 403)

        access_token = create_access_token(user.id)
        refresh_token, _jti, refresh_expires_at = create_refresh_token(user.id)
        await self.repository.save_refresh_token(
            user.id, hash_token(refresh_token), refresh_expires_at, device_info
        )
        user.last_login_at = utc_now()
        await self.session.commit()
        await self.session.refresh(user)
        return user, access_token, refresh_token, refresh_expires_at

    async def refresh(self, refresh_token: str | None) -> tuple[User, str, str, datetime]:
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
        if not user:
            raise AppError("AUTH_REFRESH_TOKEN_INVALID", "유효하지 않은 Refresh Token입니다.", 401)
        if user.status != UserStatus.ACTIVE:
            raise AppError("AUTH_USER_INACTIVE", "비활성 사용자입니다.", 403)

        stored_token.revoked_at = utc_now()
        new_refresh_token, _jti, refresh_expires_at = create_refresh_token(user.id)
        await self.repository.save_refresh_token(
            user.id, hash_token(new_refresh_token), refresh_expires_at, stored_token.device_info
        )
        await self.session.commit()
        return user, create_access_token(user.id), new_refresh_token, refresh_expires_at

    async def logout(self, refresh_token: str | None) -> None:
        if refresh_token:
            stored_token = await self.repository.get_refresh_token(hash_token(refresh_token))
            if stored_token and stored_token.revoked_at is None:
                stored_token.revoked_at = utc_now()
                await self.session.commit()

    async def get_active_user(self, user_id: int) -> User:
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise AppError("AUTH_UNAUTHORIZED", "인증이 필요합니다.", 401)
        if user.status != UserStatus.ACTIVE:
            raise AppError("AUTH_USER_INACTIVE", "비활성 사용자입니다.", 403)
        return user
