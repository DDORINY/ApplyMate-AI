from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_session
from app.models.schedule import ScheduleConfidence, ScheduleEventStatus, ScheduleEventType
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.schedule import (
    ScheduleConflictItem,
    ScheduleEventCreate,
    ScheduleEventHistoryPublic,
    ScheduleEventListData,
    ScheduleEventPublic,
    ScheduleEventUpdate,
    ScheduleOptionsData,
    ScheduleReminderCreate,
    ScheduleReminderPublic,
    ScheduleReminderUpdate,
    ScheduleStatusChange,
    ScheduleUpcomingData,
)
from app.services.schedule import ScheduleService

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/options", response_model=ApiResponse[ScheduleOptionsData])
async def calendar_options(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ScheduleOptionsData]:
    data = await ScheduleService(session).options(current_user.id)
    return ApiResponse(success=True, data=data, message="일정 선택 옵션입니다.")


@router.post("/events", response_model=ApiResponse[ScheduleEventPublic], status_code=status.HTTP_201_CREATED)
async def create_calendar_event(
    payload: ScheduleEventCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ScheduleEventPublic]:
    data = await ScheduleService(session).create_event(current_user.id, payload)
    return ApiResponse(success=True, data=data, message="일정이 생성되었습니다.")


@router.get("/events", response_model=ApiResponse[ScheduleEventListData])
async def list_calendar_events(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    start_from: datetime | None = None,
    start_to: datetime | None = None,
    event_type: ScheduleEventType | None = None,
    status_filter: ScheduleEventStatus | None = Query(default=None, alias="status"),
    confidence: ScheduleConfidence | None = None,
    application_id: int | None = None,
    job_id: int | None = None,
    has_reminder: bool | None = None,
    include_archived: bool = False,
    keyword: str | None = None,
    sort: str = "start_at",
    order: str = "asc",
) -> ApiResponse[ScheduleEventListData]:
    data = await ScheduleService(session).list_events(
        current_user.id,
        page=page,
        size=size,
        start_from=start_from,
        start_to=start_to,
        event_type=event_type,
        status=status_filter,
        confidence=confidence,
        application_id=application_id,
        job_id=job_id,
        has_reminder=has_reminder,
        include_archived=include_archived,
        keyword=keyword,
        sort=sort,
        order=order,
    )
    return ApiResponse(success=True, data=data, message="일정 목록입니다.")


@router.get("/upcoming", response_model=ApiResponse[ScheduleUpcomingData])
async def upcoming_calendar_events(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    hours: int = Query(default=168, ge=1, le=24 * 60),
    size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[ScheduleUpcomingData]:
    data = await ScheduleService(session).upcoming(current_user.id, hours=hours, size=size)
    return ApiResponse(success=True, data=data, message="다가오는 일정입니다.")


@router.get("/conflicts", response_model=ApiResponse[list[ScheduleConflictItem]])
async def calendar_conflicts(
    start_at: datetime,
    end_at: datetime,
    exclude_event_id: int | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ScheduleConflictItem]]:
    data = await ScheduleService(session).conflicts(current_user.id, start_at, end_at, exclude_event_id)
    return ApiResponse(success=True, data=data, message="일정 충돌 목록입니다.")


@router.get("/events/{event_id}", response_model=ApiResponse[ScheduleEventPublic])
async def get_calendar_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ScheduleEventPublic]:
    data = await ScheduleService(session).get_event(current_user.id, event_id)
    return ApiResponse(success=True, data=data, message="일정 상세입니다.")


@router.patch("/events/{event_id}", response_model=ApiResponse[ScheduleEventPublic])
async def update_calendar_event(
    event_id: int,
    payload: ScheduleEventUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ScheduleEventPublic]:
    data = await ScheduleService(session).update_event(current_user.id, event_id, payload)
    return ApiResponse(success=True, data=data, message="일정이 수정되었습니다.")


@router.delete("/events/{event_id}", response_model=ApiResponse[dict[str, bool]])
async def archive_calendar_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, bool]]:
    data = await ScheduleService(session).archive_event(current_user.id, event_id)
    return ApiResponse(success=True, data=data, message="일정이 보관되었습니다.")


@router.post("/events/{event_id}/status", response_model=ApiResponse[ScheduleEventPublic])
async def change_calendar_event_status(
    event_id: int,
    payload: ScheduleStatusChange,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ScheduleEventPublic]:
    data = await ScheduleService(session).change_status(current_user.id, event_id, payload)
    return ApiResponse(success=True, data=data, message="일정 상태가 변경되었습니다.")


@router.get("/events/{event_id}/history", response_model=ApiResponse[list[ScheduleEventHistoryPublic]])
async def list_calendar_event_history(
    event_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ScheduleEventHistoryPublic]]:
    data = await ScheduleService(session).list_history(current_user.id, event_id)
    return ApiResponse(success=True, data=data, message="일정 변경 이력입니다.")


@router.post("/events/{event_id}/reminders", response_model=ApiResponse[ScheduleReminderPublic], status_code=status.HTTP_201_CREATED)
async def create_calendar_event_reminder(
    event_id: int,
    payload: ScheduleReminderCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ScheduleReminderPublic]:
    data = await ScheduleService(session).create_reminder(current_user.id, event_id, payload)
    return ApiResponse(success=True, data=data, message="일정 알림이 생성되었습니다.")


@router.get("/events/{event_id}/reminders", response_model=ApiResponse[list[ScheduleReminderPublic]])
async def list_calendar_event_reminders(
    event_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ScheduleReminderPublic]]:
    data = await ScheduleService(session).list_reminders(current_user.id, event_id)
    return ApiResponse(success=True, data=data, message="일정 알림 목록입니다.")


@router.patch("/events/{event_id}/reminders/{reminder_id}", response_model=ApiResponse[ScheduleReminderPublic])
async def update_calendar_event_reminder(
    event_id: int,
    reminder_id: int,
    payload: ScheduleReminderUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ScheduleReminderPublic]:
    data = await ScheduleService(session).update_reminder(current_user.id, event_id, reminder_id, payload)
    return ApiResponse(success=True, data=data, message="일정 알림이 수정되었습니다.")


@router.delete("/events/{event_id}/reminders/{reminder_id}", response_model=ApiResponse[dict[str, bool]])
async def delete_calendar_event_reminder(
    event_id: int,
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, bool]]:
    data = await ScheduleService(session).delete_reminder(current_user.id, event_id, reminder_id)
    return ApiResponse(success=True, data=data, message="일정 알림이 삭제되었습니다.")
