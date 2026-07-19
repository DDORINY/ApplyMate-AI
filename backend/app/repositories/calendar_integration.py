from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.integration import (
    CalendarConnection,
    CalendarConnectionStatus,
    CalendarOAuthState,
    CalendarSyncMapping,
    ExternalAccount,
    ExternalAccountPurpose,
    ExternalProvider,
    SyncError,
    SyncRun,
)
from app.models.schedule import ScheduleEvent, ScheduleEventStatus


class CalendarIntegrationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_state(
        self,
        *,
        user_id: int,
        provider: ExternalProvider,
        state_hash: str,
        redirect_path: str,
        expires_at: datetime,
    ) -> CalendarOAuthState:
        item = CalendarOAuthState(
            user_id=user_id,
            provider=provider,
            state_hash=state_hash,
            redirect_path=redirect_path,
            expires_at=expires_at,
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_state(self, state_hash: str) -> CalendarOAuthState | None:
        return await self.session.scalar(select(CalendarOAuthState).where(CalendarOAuthState.state_hash == state_hash))

    async def get_external_account(self, user_id: int) -> ExternalAccount | None:
        result = await self.session.execute(
            select(ExternalAccount)
            .where(
                ExternalAccount.user_id == user_id,
                ExternalAccount.provider == ExternalProvider.GOOGLE,
                ExternalAccount.purpose == ExternalAccountPurpose.CALENDAR,
            )
            .order_by(ExternalAccount.id.desc())
        )
        return result.scalar_one_or_none()

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
        token_expires_at: datetime | None,
        token_version: str,
        now: datetime,
    ) -> ExternalAccount:
        account = await self.get_external_account(user_id)
        if account is None:
            account = ExternalAccount(
                user_id=user_id,
                provider=ExternalProvider.GOOGLE,
                purpose=ExternalAccountPurpose.CALENDAR,
                provider_account_id=provider_account_id,
                connected_at=now,
            )
            self.session.add(account)
        account.provider_account_id = provider_account_id
        account.email = email
        account.display_name = display_name
        account.scopes = scopes
        account.access_token_encrypted = access_token_encrypted
        account.refresh_token_encrypted = refresh_token_encrypted
        account.token_expires_at = token_expires_at
        account.token_version = token_version
        account.is_active = True
        account.disconnected_at = None
        await self.session.flush()
        return account

    async def get_connection(self, user_id: int) -> CalendarConnection | None:
        result = await self.session.execute(
            select(CalendarConnection)
            .options(selectinload(CalendarConnection.external_account))
            .where(CalendarConnection.user_id == user_id, CalendarConnection.provider == ExternalProvider.GOOGLE)
            .order_by(CalendarConnection.id.desc())
        )
        return result.scalar_one_or_none()

    async def upsert_connection(self, *, user_id: int, account: ExternalAccount, now: datetime) -> CalendarConnection:
        connection = await self.get_connection(user_id)
        if connection is None:
            connection = CalendarConnection(
                user_id=user_id,
                external_account_id=account.id,
                provider=ExternalProvider.GOOGLE,
                connected_at=now,
            )
            self.session.add(connection)
        connection.external_account_id = account.id
        connection.status = CalendarConnectionStatus.ACTIVE
        connection.sync_enabled = True
        connection.disconnected_at = None
        await self.session.flush()
        return connection

    async def get_schedule_event(self, user_id: int, event_id: int) -> ScheduleEvent | None:
        return await self.session.scalar(
            select(ScheduleEvent).where(
                ScheduleEvent.id == event_id,
                ScheduleEvent.user_id == user_id,
                ScheduleEvent.is_archived.is_(False),
            )
        )

    async def list_syncable_events(self, user_id: int) -> list[ScheduleEvent]:
        result = await self.session.execute(
            select(ScheduleEvent)
            .where(
                ScheduleEvent.user_id == user_id,
                ScheduleEvent.is_archived.is_(False),
                ScheduleEvent.status != ScheduleEventStatus.CANCELLED,
            )
            .order_by(ScheduleEvent.start_at.asc(), ScheduleEvent.id.asc())
            .limit(100)
        )
        return list(result.scalars().all())

    async def get_mapping(self, user_id: int, connection_id: int, event_id: int) -> CalendarSyncMapping | None:
        return await self.session.scalar(
            select(CalendarSyncMapping).where(
                CalendarSyncMapping.user_id == user_id,
                CalendarSyncMapping.connection_id == connection_id,
                CalendarSyncMapping.schedule_event_id == event_id,
            )
        )

    async def list_mappings(self, user_id: int, connection_id: int) -> list[CalendarSyncMapping]:
        result = await self.session.execute(
            select(CalendarSyncMapping)
            .where(CalendarSyncMapping.user_id == user_id, CalendarSyncMapping.connection_id == connection_id)
            .order_by(CalendarSyncMapping.updated_at.desc(), CalendarSyncMapping.id.desc())
        )
        return list(result.scalars().all())

    async def list_sync_runs(self, user_id: int, connection_id: int, *, limit: int = 20) -> list[SyncRun]:
        result = await self.session.execute(
            select(SyncRun)
            .where(SyncRun.user_id == user_id, SyncRun.connection_id == connection_id)
            .order_by(SyncRun.started_at.desc(), SyncRun.id.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_errors(self, user_id: int, *, limit: int = 20) -> list[SyncError]:
        result = await self.session.execute(
            select(SyncError)
            .where(SyncError.user_id == user_id)
            .order_by(SyncError.created_at.desc(), SyncError.id.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
