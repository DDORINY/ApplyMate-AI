from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import utc_now
from app.models.account_security import (
    EmailVerificationToken,
    PasswordResetToken,
    SecurityEvent,
    SecurityEventType,
)


class AccountSecurityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_email_verification_token(
        self, user_id: int, token_hash: str, expires_at
    ) -> EmailVerificationToken:
        token = EmailVerificationToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.session.add(token)
        await self.session.flush()
        return token

    async def latest_email_verification_token(self, user_id: int) -> EmailVerificationToken | None:
        result = await self.session.execute(
            select(EmailVerificationToken)
            .where(EmailVerificationToken.user_id == user_id)
            .order_by(EmailVerificationToken.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_email_verification_token(self, token_hash: str) -> EmailVerificationToken | None:
        result = await self.session.execute(
            select(EmailVerificationToken).where(EmailVerificationToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def mark_unused_email_tokens_used(self, user_id: int) -> None:
        result = await self.session.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.used_at.is_(None),
            )
        )
        now = utc_now()
        for token in result.scalars().all():
            token.used_at = now

    async def create_password_reset_token(
        self, user_id: int, token_hash: str, expires_at
    ) -> PasswordResetToken:
        token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_password_reset_token(self, token_hash: str) -> PasswordResetToken | None:
        result = await self.session.execute(
            select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def mark_unused_password_reset_tokens_used(self, user_id: int) -> None:
        result = await self.session.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used_at.is_(None),
            )
        )
        now = utc_now()
        for token in result.scalars().all():
            token.used_at = now

    async def create_security_event(
        self,
        event_type: SecurityEventType,
        user_id: int | None = None,
        session_id: str | None = None,
        ip_address_hash: str | None = None,
        user_agent: str | None = None,
        event_metadata: dict[str, object] | None = None,
    ) -> SecurityEvent:
        event = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            session_id=session_id,
            ip_address_hash=ip_address_hash,
            user_agent=user_agent,
            event_metadata=event_metadata or {},
        )
        self.session.add(event)
        await self.session.flush()
        return event

    async def list_security_events(self, user_id: int, limit: int = 20) -> list[SecurityEvent]:
        result = await self.session.execute(
            select(SecurityEvent)
            .where(SecurityEvent.user_id == user_id)
            .order_by(SecurityEvent.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
