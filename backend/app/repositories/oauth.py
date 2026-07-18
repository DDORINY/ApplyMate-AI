from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.oauth import OAuthAccount, OAuthLoginTicket, OAuthProvider, OAuthPurpose, OAuthState


class OAuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_account_by_provider_user(
        self, provider: OAuthProvider, provider_user_id: str
    ) -> OAuthAccount | None:
        result = await self.session.execute(
            select(OAuthAccount).where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_provider_account(
        self, user_id: int, provider: OAuthProvider
    ) -> OAuthAccount | None:
        result = await self.session.execute(
            select(OAuthAccount).where(
                OAuthAccount.user_id == user_id,
                OAuthAccount.provider == provider,
            )
        )
        return result.scalar_one_or_none()

    async def list_accounts(self, user_id: int) -> list[OAuthAccount]:
        result = await self.session.execute(
            select(OAuthAccount)
            .where(OAuthAccount.user_id == user_id)
            .order_by(OAuthAccount.provider)
        )
        return list(result.scalars())

    async def count_accounts(self, user_id: int) -> int:
        return len(await self.list_accounts(user_id))

    async def create_account(
        self,
        user_id: int,
        provider: OAuthProvider,
        provider_user_id: str,
        provider_email: str | None,
        provider_username: str | None,
        provider_display_name: str | None,
        email_verified: bool,
    ) -> OAuthAccount:
        account = OAuthAccount(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_email=provider_email,
            provider_username=provider_username,
            provider_display_name=provider_display_name,
            email_verified=email_verified,
        )
        self.session.add(account)
        await self.session.flush()
        await self.session.refresh(account)
        return account

    async def create_state(
        self,
        state_hash: str,
        provider: OAuthProvider,
        purpose: OAuthPurpose,
        user_id: int | None,
        redirect_path: str,
        expires_at: datetime,
    ) -> OAuthState:
        state = OAuthState(
            state_hash=state_hash,
            provider=provider,
            purpose=purpose,
            user_id=user_id,
            redirect_path=redirect_path,
            expires_at=expires_at,
        )
        self.session.add(state)
        await self.session.flush()
        return state

    async def get_state(self, state_hash: str) -> OAuthState | None:
        result = await self.session.execute(
            select(OAuthState).where(OAuthState.state_hash == state_hash)
        )
        return result.scalar_one_or_none()

    async def create_ticket(
        self,
        ticket_hash: str,
        user_id: int,
        provider: OAuthProvider,
        redirect_path: str,
        expires_at: datetime,
    ) -> OAuthLoginTicket:
        ticket = OAuthLoginTicket(
            ticket_hash=ticket_hash,
            user_id=user_id,
            provider=provider,
            redirect_path=redirect_path,
            expires_at=expires_at,
        )
        self.session.add(ticket)
        await self.session.flush()
        return ticket

    async def get_ticket(self, ticket_hash: str) -> OAuthLoginTicket | None:
        result = await self.session.execute(
            select(OAuthLoginTicket).where(OAuthLoginTicket.ticket_hash == ticket_hash)
        )
        return result.scalar_one_or_none()
