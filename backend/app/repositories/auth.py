from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import utc_now
from app.models.refresh_token import RefreshToken
from app.models.user import User


class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def create_user(
        self, email: str, password_hash: str | None, name: str, email_verified: bool = False
    ) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
            name=name,
            email_verified=email_verified,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def save_refresh_token(
        self,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        session_id: str,
        device_info: str | None,
        device_name: str | None,
        user_agent: str | None,
        ip_address_hash: str | None,
        last_used_at: datetime | None = None,
    ) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            session_id=session_id,
            device_info=device_info,
            device_name=device_name,
            user_agent=user_agent,
            ip_address_hash=ip_address_hash,
            last_used_at=last_used_at,
        )
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_refresh_token(self, token_hash: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def list_active_refresh_tokens(self, user_id: int) -> list[RefreshToken]:
        result = await self.session.execute(
            select(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > utc_now(),
            )
            .order_by(RefreshToken.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_active_session(self, user_id: int, session_id: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.session_id == session_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > utc_now(),
            )
            .order_by(RefreshToken.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def revoke_session(self, user_id: int, session_id: str) -> int:
        result = await self.session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.session_id == session_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=utc_now())
        )
        return result.rowcount or 0

    async def revoke_other_sessions(self, user_id: int, current_session_id: str) -> int:
        result = await self.session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.session_id != current_session_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=utc_now())
        )
        return result.rowcount or 0

    async def revoke_all_sessions(self, user_id: int) -> int:
        result = await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=utc_now())
        )
        return result.rowcount or 0
