from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application
from app.models.email_analysis import (
    EmailCandidate,
    EmailMessage,
    EmailSyncRun,
    GmailConnection,
    GmailOAuthState,
)
from app.models.integration import ExternalAccount, ExternalAccountPurpose, ExternalProvider


class GmailIntegrationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_state(self, *, user_id: int, provider: ExternalProvider, state_hash: str, redirect_path: str, expires_at) -> GmailOAuthState:
        state = GmailOAuthState(user_id=user_id, provider=provider, state_hash=state_hash, redirect_path=redirect_path, expires_at=expires_at)
        self.session.add(state)
        return state

    async def get_state(self, state_hash: str) -> GmailOAuthState | None:
        return await self.session.scalar(select(GmailOAuthState).where(GmailOAuthState.state_hash == state_hash))

    async def get_connection(self, user_id: int) -> GmailConnection | None:
        return await self.session.scalar(
            select(GmailConnection)
            .options(selectinload(GmailConnection.external_account))
            .where(GmailConnection.user_id == user_id)
            .order_by(GmailConnection.id.desc())
        )

    async def upsert_external_account(
        self,
        *,
        user_id: int,
        provider_account_id: str,
        email: str | None,
        display_name: str | None,
        scopes: str,
        access_token_encrypted: str,
        refresh_token_encrypted: str | None,
        token_expires_at,
        token_version: str,
        now,
    ) -> ExternalAccount:
        account = await self.session.scalar(
            select(ExternalAccount).where(
                ExternalAccount.user_id == user_id,
                ExternalAccount.provider == ExternalProvider.GOOGLE,
                ExternalAccount.purpose == ExternalAccountPurpose.GMAIL,
            )
        )
        if account is None:
            account = ExternalAccount(
                user_id=user_id,
                provider=ExternalProvider.GOOGLE,
                purpose=ExternalAccountPurpose.GMAIL,
                provider_account_id=provider_account_id,
                email=email,
                display_name=display_name,
                scopes=scopes,
                access_token_encrypted=access_token_encrypted,
                refresh_token_encrypted=refresh_token_encrypted,
                token_expires_at=token_expires_at,
                token_version=token_version,
                connected_at=now,
            )
            self.session.add(account)
        else:
            account.provider_account_id = provider_account_id
            account.email = email
            account.display_name = display_name
            account.scopes = scopes
            account.access_token_encrypted = access_token_encrypted
            account.refresh_token_encrypted = refresh_token_encrypted
            account.token_expires_at = token_expires_at
            account.token_version = token_version
            account.is_active = True
            account.connected_at = now
            account.disconnected_at = None
        await self.session.flush()
        return account

    async def get_message_by_provider_id(self, connection_id: int, provider_message_id: str) -> EmailMessage | None:
        return await self.session.scalar(
            select(EmailMessage).where(
                EmailMessage.connection_id == connection_id,
                EmailMessage.provider_message_id == provider_message_id,
            )
        )

    async def list_candidates(
        self,
        user_id: int,
        *,
        page: int,
        size: int,
        status=None,
        candidate_type=None,
    ) -> tuple[list[EmailCandidate], int]:
        query = (
            select(EmailCandidate)
            .options(selectinload(EmailCandidate.email_message))
            .where(EmailCandidate.user_id == user_id)
        )
        if status is not None:
            query = query.where(EmailCandidate.status == status)
        if candidate_type is not None:
            query = query.where(EmailCandidate.candidate_type == candidate_type)
        total = int((await self.session.execute(select(func.count()).select_from(query.order_by(None).subquery()))).scalar_one())
        result = await self.session.execute(
            query.order_by(EmailCandidate.created_at.desc(), EmailCandidate.id.desc()).offset((page - 1) * size).limit(size)
        )
        return list(result.scalars().unique().all()), total

    async def get_candidate(self, user_id: int, candidate_id: int) -> EmailCandidate | None:
        return await self.session.scalar(
            select(EmailCandidate)
            .options(selectinload(EmailCandidate.email_message), selectinload(EmailCandidate.actions))
            .where(EmailCandidate.id == candidate_id, EmailCandidate.user_id == user_id)
        )

    async def list_sync_runs(self, user_id: int, connection_id: int) -> list[EmailSyncRun]:
        result = await self.session.execute(
            select(EmailSyncRun)
            .where(EmailSyncRun.user_id == user_id, EmailSyncRun.connection_id == connection_id)
            .order_by(EmailSyncRun.started_at.desc(), EmailSyncRun.id.desc())
            .limit(20)
        )
        return list(result.scalars().all())

    async def get_sync_run(self, user_id: int, connection_id: int, run_id: int) -> EmailSyncRun | None:
        return await self.session.scalar(
            select(EmailSyncRun).where(
                EmailSyncRun.id == run_id,
                EmailSyncRun.user_id == user_id,
                EmailSyncRun.connection_id == connection_id,
            )
        )

    async def list_application_options(self, user_id: int, company: str | None, job_title: str | None) -> list[Application]:
        query = select(Application).where(Application.user_id == user_id, Application.is_archived.is_(False))
        filters = []
        if company:
            filters.append(func.lower(Application.company_name_snapshot).like(f"%{company.lower()}%"))
        if job_title:
            filters.append(func.lower(Application.job_title_snapshot).like(f"%{job_title.lower()}%"))
        if filters:
            query = query.where(or_(*filters))
        result = await self.session.execute(query.order_by(Application.updated_at.desc(), Application.id.desc()).limit(10))
        return list(result.scalars().all())
