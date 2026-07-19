from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.calendar_integration import (
    CalendarCallbackData,
    CalendarConnectData,
    CalendarConnectRequest,
    CalendarIntegrationStatusData,
    CalendarSettingsUpdate,
    CalendarSyncErrorPublic,
    CalendarSyncResult,
    CalendarSyncRunPublic,
    EventSyncStatusData,
    ExternalCalendarPublic,
)
from app.schemas.common import ApiResponse
from app.services.calendar_integration import CalendarIntegrationService

router = APIRouter(tags=["calendar-integration"])


@router.get("/integrations/calendar/status", response_model=ApiResponse[CalendarIntegrationStatusData])
async def calendar_integration_status(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[CalendarIntegrationStatusData]:
    data = await CalendarIntegrationService(session).status(current_user.id)
    return ApiResponse(success=True, data=data, message="Calendar integration status returned.")


@router.post("/integrations/calendar/connect", response_model=ApiResponse[CalendarConnectData])
async def connect_calendar(
    payload: CalendarConnectRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[CalendarConnectData]:
    data = await CalendarIntegrationService(session).connect(current_user.id, payload.redirect_path)
    return ApiResponse(success=True, data=data, message="Calendar authorization URL created.")


@router.get("/integrations/calendar/callback", response_model=ApiResponse[CalendarCallbackData])
async def calendar_callback(
    state: str | None = None,
    code: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[CalendarCallbackData]:
    data = await CalendarIntegrationService(session).callback(state, code)
    return ApiResponse(success=True, data=data, message="Calendar connection completed.")


@router.get("/integrations/calendar/calendars", response_model=ApiResponse[list[ExternalCalendarPublic]])
async def list_calendars(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ExternalCalendarPublic]]:
    data = await CalendarIntegrationService(session).list_calendars(current_user.id)
    return ApiResponse(success=True, data=data, message="Calendar list returned.")


@router.patch("/integrations/calendar/settings", response_model=ApiResponse[CalendarIntegrationStatusData])
async def update_calendar_settings(
    payload: CalendarSettingsUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[CalendarIntegrationStatusData]:
    data = await CalendarIntegrationService(session).update_settings(current_user.id, payload)
    return ApiResponse(success=True, data=data, message="Calendar integration settings updated.")


@router.delete("/integrations/calendar/connection", response_model=ApiResponse[dict[str, bool]])
async def disconnect_calendar(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, bool]]:
    data = await CalendarIntegrationService(session).disconnect(current_user.id)
    return ApiResponse(success=True, data=data, message="Calendar connection disconnected.")


@router.post("/integrations/calendar/sync", response_model=ApiResponse[CalendarSyncResult])
async def sync_calendar(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[CalendarSyncResult]:
    data = await CalendarIntegrationService(session).sync_all(current_user.id)
    return ApiResponse(success=True, data=data, message="Calendar sync completed.")


@router.get("/integrations/calendar/sync-runs", response_model=ApiResponse[list[CalendarSyncRunPublic]])
async def list_calendar_sync_runs(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[CalendarSyncRunPublic]]:
    data = await CalendarIntegrationService(session).list_sync_runs(current_user.id)
    return ApiResponse(success=True, data=data, message="Calendar sync runs returned.")


@router.get("/integrations/calendar/errors", response_model=ApiResponse[list[CalendarSyncErrorPublic]])
async def list_calendar_sync_errors(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[list[CalendarSyncErrorPublic]]:
    data = await CalendarIntegrationService(session).list_errors(current_user.id)
    return ApiResponse(success=True, data=data[:limit], message="Calendar sync errors returned.")


@router.post(
    "/calendar/events/{event_id}/sync",
    response_model=ApiResponse[CalendarSyncResult],
    status_code=status.HTTP_200_OK,
)
async def sync_calendar_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[CalendarSyncResult]:
    data = await CalendarIntegrationService(session).sync_event(current_user.id, event_id)
    return ApiResponse(success=True, data=data, message="Calendar event sync completed.")


@router.get("/calendar/events/{event_id}/sync-status", response_model=ApiResponse[EventSyncStatusData])
async def calendar_event_sync_status(
    event_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[EventSyncStatusData]:
    data = await CalendarIntegrationService(session).event_sync_status(current_user.id, event_id)
    return ApiResponse(success=True, data=data, message="Calendar event sync status returned.")
