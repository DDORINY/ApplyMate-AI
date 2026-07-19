import hashlib
import json
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.security import hash_token
from app.integrations.calendar import get_calendar_provider
from app.integrations.calendar.base import ExternalCalendar, ExternalCalendarEvent
from app.models.integration import (
    CalendarConnection,
    CalendarConnectionStatus,
    CalendarSyncDirection,
    CalendarSyncMapping,
    CalendarSyncStatus,
    ExternalProvider,
    SyncError,
    SyncErrorCode,
    SyncRun,
    SyncRunStatus,
)
from app.models.schedule import ScheduleEvent
from app.repositories.calendar_integration import CalendarIntegrationRepository
from app.schemas.calendar_integration import (
    CalendarCallbackData,
    CalendarConnectData,
    CalendarIntegrationStatusData,
    CalendarSettingsUpdate,
    CalendarSyncErrorPublic,
    CalendarSyncMappingPublic,
    CalendarSyncResult,
    CalendarSyncRunPublic,
    EventSyncStatusData,
    ExternalCalendarPublic,
)
from app.services.external_token import ExternalTokenCipher


class CalendarIntegrationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = CalendarIntegrationRepository(session)
        self.cipher = ExternalTokenCipher()

    async def status(self, user_id: int) -> CalendarIntegrationStatusData:
        settings = get_settings()
        connection = await self.repository.get_connection(user_id)
        if connection is None or not connection.external_account.is_active:
            return CalendarIntegrationStatusData(
                connected=False,
                provider=settings.calendar_provider,
                needs_verification=settings.calendar_provider == "google",
            )
        account = connection.external_account
        return CalendarIntegrationStatusData(
            connected=connection.status != CalendarConnectionStatus.DISCONNECTED,
            provider=connection.provider.value,
            email=account.email,
            display_name=account.display_name,
            scopes=self._scopes(account.scopes),
            selected_calendar_id=connection.selected_calendar_id,
            selected_calendar_name=connection.selected_calendar_name,
            selected_calendar_timezone=connection.selected_calendar_timezone,
            sync_direction=connection.sync_direction,
            sync_enabled=connection.sync_enabled,
            status=connection.status,
            last_sync_at=connection.last_sync_at,
            needs_verification=settings.calendar_provider == "google",
        )

    async def connect(self, user_id: int, redirect_path: str) -> CalendarConnectData:
        self._ensure_safe_redirect(redirect_path)
        settings = get_settings()
        state = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + timedelta(seconds=settings.calendar_oauth_state_expire_seconds)
        await self.repository.create_state(
            user_id=user_id,
            provider=ExternalProvider.GOOGLE,
            state_hash=hash_token(state),
            redirect_path=redirect_path,
            expires_at=expires_at,
        )
        await self.session.commit()
        provider = get_calendar_provider()
        scopes = list(settings.google_calendar_scopes)
        url = provider.authorization_url(state=state, redirect_uri=settings.google_calendar_redirect_uri, scopes=scopes)
        return CalendarConnectData(authorization_url=url, state=state, provider="GOOGLE", scopes=scopes)

    async def callback(self, state: str | None, code: str | None) -> CalendarCallbackData:
        if not state:
            raise AppError("CALENDAR_OAUTH_STATE_INVALID", "Calendar OAuth state is required.", 400)
        if not code:
            raise AppError("CALENDAR_OAUTH_CALLBACK_FAILED", "Calendar OAuth code is required.", 400)
        oauth_state = await self.repository.get_state(hash_token(state))
        now = datetime.now(UTC)
        if oauth_state is None or oauth_state.consumed_at is not None:
            raise AppError("CALENDAR_OAUTH_STATE_INVALID", "Calendar OAuth state is invalid.", 400)
        if self._as_utc(oauth_state.expires_at) < now:
            raise AppError("CALENDAR_OAUTH_STATE_EXPIRED", "Calendar OAuth state is expired.", 400)
        oauth_state.consumed_at = now
        token = await get_calendar_provider().exchange_code(code=code, redirect_uri=get_settings().google_calendar_redirect_uri)
        encrypted_access = self.cipher.encrypt(token.access_token)
        encrypted_refresh = self.cipher.encrypt(token.refresh_token) if token.refresh_token else None
        scopes = token.scopes or list(get_settings().google_calendar_scopes)
        account = await self.repository.upsert_external_account(
            user_id=oauth_state.user_id,
            provider_account_id=token.provider_account_id,
            email=token.email,
            display_name=token.display_name,
            scopes=" ".join(scopes),
            access_token_encrypted=encrypted_access,
            refresh_token_encrypted=encrypted_refresh,
            token_expires_at=token.expires_at,
            token_version=get_settings().external_token_encryption_key_version,
            now=now,
        )
        connection = await self.repository.upsert_connection(user_id=oauth_state.user_id, account=account, now=now)
        calendars = await self._calendars_for_connection(connection)
        primary = next((item for item in calendars if item.primary and item.writable), None)
        if primary:
            self._apply_calendar(connection, primary)
        await self.session.commit()
        return CalendarCallbackData(
            connected=True,
            connection_id=connection.id,
            provider=connection.provider.value,
            email=account.email,
        )

    async def list_calendars(self, user_id: int) -> list[ExternalCalendarPublic]:
        connection = await self._active_connection(user_id)
        calendars = await self._calendars_for_connection(connection)
        return [
            ExternalCalendarPublic(
                id=item.id,
                name=item.name,
                timezone=item.timezone,
                primary=item.primary,
                access_role=item.access_role,
                writable=item.writable,
                selected=item.id == connection.selected_calendar_id,
            )
            for item in calendars
        ]

    async def update_settings(self, user_id: int, payload: CalendarSettingsUpdate) -> CalendarIntegrationStatusData:
        connection = await self._active_connection(user_id)
        if payload.selected_calendar_id is not None:
            calendars = await self._calendars_for_connection(connection)
            selected = next((item for item in calendars if item.id == payload.selected_calendar_id), None)
            if selected is None:
                raise AppError("CALENDAR_LIST_FAILED", "Selected calendar was not found.", 404)
            if not selected.writable:
                raise AppError("CALENDAR_NOT_WRITABLE", "Selected calendar is not writable.", 400)
            self._apply_calendar(connection, selected)
        if payload.sync_direction is not None:
            connection.sync_direction = payload.sync_direction
        if payload.sync_enabled is not None:
            connection.sync_enabled = payload.sync_enabled
        await self.session.commit()
        return await self.status(user_id)

    async def disconnect(self, user_id: int) -> dict[str, bool]:
        connection = await self._active_connection(user_id)
        account = connection.external_account
        try:
            await get_calendar_provider().revoke_token(token=self.cipher.decrypt(account.access_token_encrypted))
        except AppError:
            pass
        now = datetime.now(UTC)
        connection.status = CalendarConnectionStatus.DISCONNECTED
        connection.sync_enabled = False
        connection.disconnected_at = now
        account.is_active = False
        account.disconnected_at = now
        account.access_token_encrypted = self.cipher.encrypt("revoked")
        account.refresh_token_encrypted = None
        await self.session.commit()
        return {"disconnected": True}

    async def sync_all(self, user_id: int) -> CalendarSyncResult:
        connection = await self._active_connection(user_id)
        self._ensure_syncable(connection)
        events = await self.repository.list_syncable_events(user_id)
        return await self._sync_events(user_id, connection, events)

    async def sync_event(self, user_id: int, event_id: int) -> CalendarSyncResult:
        connection = await self._active_connection(user_id)
        self._ensure_syncable(connection)
        event = await self.repository.get_schedule_event(user_id, event_id)
        if event is None:
            raise AppError("SCHEDULE_EVENT_NOT_FOUND", "Schedule event was not found.", 404)
        return await self._sync_events(user_id, connection, [event])

    async def event_sync_status(self, user_id: int, event_id: int) -> EventSyncStatusData:
        connection = await self.repository.get_connection(user_id)
        if connection is None or connection.status == CalendarConnectionStatus.DISCONNECTED:
            return EventSyncStatusData(connected=False)
        mapping = await self.repository.get_mapping(user_id, connection.id, event_id)
        errors = await self.repository.list_errors(user_id, limit=1)
        return EventSyncStatusData(
            connected=True,
            mapping=CalendarSyncMappingPublic.model_validate(mapping) if mapping else None,
            last_error=CalendarSyncErrorPublic.model_validate(errors[0]) if errors else None,
        )

    async def list_sync_runs(self, user_id: int) -> list[CalendarSyncRunPublic]:
        connection = await self._active_connection(user_id)
        runs = await self.repository.list_sync_runs(user_id, connection.id)
        return [CalendarSyncRunPublic.model_validate(item) for item in runs]

    async def list_errors(self, user_id: int) -> list[CalendarSyncErrorPublic]:
        errors = await self.repository.list_errors(user_id)
        return [CalendarSyncErrorPublic.model_validate(item) for item in errors]

    async def _sync_events(
        self, user_id: int, connection: CalendarConnection, events: list[ScheduleEvent]
    ) -> CalendarSyncResult:
        now = datetime.now(UTC)
        run = SyncRun(
            user_id=user_id,
            connection_id=connection.id,
            direction=connection.sync_direction,
            status=SyncRunStatus.RUNNING,
            started_at=now,
        )
        self.session.add(run)
        await self.session.flush()
        mappings: list[CalendarSyncMapping] = []
        errors: list[SyncError] = []
        access_token = self.cipher.decrypt(connection.external_account.access_token_encrypted)
        provider = get_calendar_provider()
        for event in events:
            try:
                mapping = await self.repository.get_mapping(user_id, connection.id, event.id)
                if mapping:
                    external_event = await provider.update_event(
                        access_token=access_token,
                        calendar_id=connection.selected_calendar_id or "primary",
                        external_event_id=mapping.external_event_id,
                        event=event,
                    )
                    run.updated_count += 1
                else:
                    external_event = await provider.create_event(
                        access_token=access_token,
                        calendar_id=connection.selected_calendar_id or "primary",
                        event=event,
                    )
                    mapping = CalendarSyncMapping(
                        user_id=user_id,
                        connection_id=connection.id,
                        schedule_event_id=event.id,
                        external_calendar_id=connection.selected_calendar_id or "primary",
                        external_event_id=external_event.id,
                    )
                    self.session.add(mapping)
                    run.created_count += 1
                self._apply_external_event(mapping, event, external_event, now)
                mappings.append(mapping)
            except AppError as exc:
                run.error_count += 1
                error = SyncError(
                    user_id=user_id,
                    connection_id=connection.id,
                    sync_run_id=run.id,
                    error_code=SyncErrorCode.CALENDAR_SYNC_FAILED,
                    safe_message=exc.message,
                    retryable=True,
                )
                self.session.add(error)
                errors.append(error)
        run.status = SyncRunStatus.COMPLETED if run.error_count == 0 else SyncRunStatus.PARTIAL_FAILED
        run.completed_at = datetime.now(UTC)
        connection.last_sync_at = run.completed_at
        await self.session.commit()
        await self.session.refresh(run)
        return CalendarSyncResult(
            run=CalendarSyncRunPublic.model_validate(run),
            mappings=[CalendarSyncMappingPublic.model_validate(item) for item in mappings],
            errors=[CalendarSyncErrorPublic.model_validate(item) for item in errors],
        )

    async def _active_connection(self, user_id: int) -> CalendarConnection:
        connection = await self.repository.get_connection(user_id)
        if connection is None or connection.status == CalendarConnectionStatus.DISCONNECTED:
            raise AppError("CALENDAR_CONNECTION_NOT_FOUND", "Calendar connection was not found.", 404)
        if connection.status == CalendarConnectionStatus.REAUTH_REQUIRED:
            raise AppError("CALENDAR_REAUTH_REQUIRED", "Calendar connection requires reauthorization.", 409)
        return connection

    def _ensure_syncable(self, connection: CalendarConnection) -> None:
        if not connection.sync_enabled:
            raise AppError("CALENDAR_PROVIDER_DISABLED", "Calendar sync is disabled.", 409)
        if connection.sync_direction != CalendarSyncDirection.INTERNAL_TO_GOOGLE:
            raise AppError(
                "CALENDAR_SYNC_CONFLICT",
                "Only INTERNAL_TO_GOOGLE sync is available in v0.5.0.",
                409,
            )
        if not connection.selected_calendar_id:
            raise AppError("CALENDAR_LIST_FAILED", "A writable calendar must be selected before sync.", 400)

    async def _calendars_for_connection(self, connection: CalendarConnection) -> list[ExternalCalendar]:
        access_token = self.cipher.decrypt(connection.external_account.access_token_encrypted)
        calendars = await get_calendar_provider().list_calendars(access_token=access_token)
        return calendars

    def _apply_calendar(self, connection: CalendarConnection, calendar: ExternalCalendar) -> None:
        connection.selected_calendar_id = calendar.id
        connection.selected_calendar_name = calendar.name
        connection.selected_calendar_timezone = calendar.timezone

    def _apply_external_event(
        self,
        mapping: CalendarSyncMapping,
        event: ScheduleEvent,
        external_event: ExternalCalendarEvent,
        now: datetime,
    ) -> None:
        mapping.external_etag = external_event.etag
        mapping.external_updated_at = external_event.updated_at
        mapping.last_internal_hash = self._internal_hash(event)
        mapping.last_external_hash = self._external_hash(external_event)
        mapping.sync_status = CalendarSyncStatus.SYNCED
        mapping.last_synced_at = now
        mapping.updated_at = now

    def _internal_hash(self, event: ScheduleEvent) -> str:
        payload = {
            "title": event.title,
            "description": event.description,
            "event_type": event.event_type.value,
            "start_at": self._as_utc(event.start_at).isoformat(),
            "end_at": self._as_utc(event.end_at).isoformat(),
            "all_day": event.all_day,
            "timezone": event.timezone,
            "location": event.location,
            "online_url": event.online_url,
            "status": event.status.value,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def _external_hash(self, event: ExternalCalendarEvent) -> str:
        payload = {
            "id": event.id,
            "etag": event.etag,
            "updated_at": event.updated_at.isoformat() if event.updated_at else None,
            "status": event.status,
            "summary": event.summary,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def _scopes(self, value: str) -> list[str]:
        return [item for item in value.replace(",", " ").split() if item]

    def _ensure_safe_redirect(self, path: str) -> None:
        if not path.startswith("/") or path.startswith("//") or "\\" in path:
            raise AppError("CALENDAR_OAUTH_CALLBACK_FAILED", "Invalid redirect path.", 400)

    def _as_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
