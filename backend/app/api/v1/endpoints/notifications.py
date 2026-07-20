from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_session
from app.models.notification import NotificationStatus
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.notification import (
    NotificationDeliveryListData,
    NotificationDeliveryPublic,
    NotificationListData,
    NotificationProcessingRunPublic,
    NotificationPublic,
    NotificationSettingPublic,
    NotificationSettingUpdate,
    NotificationUnreadCountData,
)
from app.services.notification import NotificationService

router = APIRouter(tags=["notifications"])


@router.get("/notifications", response_model=ApiResponse[NotificationListData])
async def list_notifications(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status: NotificationStatus | None = None,
) -> ApiResponse[NotificationListData]:
    data = await NotificationService(session).list_notifications(current_user.id, page, size, status)
    return ApiResponse(success=True, data=data, message="알림 목록입니다.")


@router.get("/notifications/unread-count", response_model=ApiResponse[NotificationUnreadCountData])
async def unread_count(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[NotificationUnreadCountData]:
    data = await NotificationService(session).unread_count(current_user.id)
    return ApiResponse(success=True, data=data, message="읽지 않은 알림 수입니다.")


@router.get("/notifications/{notification_id}", response_model=ApiResponse[NotificationPublic])
async def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[NotificationPublic]:
    data = await NotificationService(session).get_notification(current_user.id, notification_id)
    return ApiResponse(success=True, data=data, message="알림 상세입니다.")


@router.patch("/notifications/{notification_id}/read", response_model=ApiResponse[NotificationPublic])
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[NotificationPublic]:
    data = await NotificationService(session).mark_read(current_user.id, notification_id)
    return ApiResponse(success=True, data=data, message="알림을 읽음 처리했습니다.")


@router.patch("/notifications/{notification_id}/dismiss", response_model=ApiResponse[NotificationPublic])
async def dismiss_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[NotificationPublic]:
    data = await NotificationService(session).dismiss(current_user.id, notification_id)
    return ApiResponse(success=True, data=data, message="알림을 해제했습니다.")


@router.patch("/notifications/{notification_id}/archive", response_model=ApiResponse[NotificationPublic])
async def archive_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[NotificationPublic]:
    data = await NotificationService(session).archive(current_user.id, notification_id)
    return ApiResponse(success=True, data=data, message="알림을 보관했습니다.")


@router.post("/notifications/read-all", response_model=ApiResponse[NotificationUnreadCountData])
async def read_all_notifications(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[NotificationUnreadCountData]:
    data = await NotificationService(session).read_all(current_user.id)
    return ApiResponse(success=True, data=data, message="모든 알림을 읽음 처리했습니다.")


@router.post("/notifications/run-due", response_model=ApiResponse[NotificationProcessingRunPublic])
async def run_due_notifications(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[NotificationProcessingRunPublic]:
    data = await NotificationService(session).run_due(current_user.id)
    return ApiResponse(success=True, data=data, message="알림 worker 작업을 실행했습니다.")


@router.get("/notification-settings", response_model=ApiResponse[NotificationSettingPublic])
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[NotificationSettingPublic]:
    data = await NotificationService(session).get_settings(current_user.id)
    return ApiResponse(success=True, data=data, message="알림 설정입니다.")


@router.patch("/notification-settings", response_model=ApiResponse[NotificationSettingPublic])
async def update_notification_settings(
    payload: NotificationSettingUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[NotificationSettingPublic]:
    data = await NotificationService(session).update_settings(current_user.id, payload)
    return ApiResponse(success=True, data=data, message="알림 설정이 수정되었습니다.")


@router.get("/notification-deliveries", response_model=ApiResponse[NotificationDeliveryListData])
async def list_notification_deliveries(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[NotificationDeliveryListData]:
    data = await NotificationService(session).list_deliveries(current_user.id, page, size)
    return ApiResponse(success=True, data=data, message="알림 delivery 목록입니다.")


@router.get("/notification-deliveries/{delivery_id}", response_model=ApiResponse[NotificationDeliveryPublic])
async def get_notification_delivery(
    delivery_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[NotificationDeliveryPublic]:
    data = await NotificationService(session).get_delivery(current_user.id, delivery_id)
    return ApiResponse(success=True, data=data, message="알림 delivery 상세입니다.")


@router.post("/notification-deliveries/{delivery_id}/retry", response_model=ApiResponse[NotificationDeliveryPublic])
async def retry_notification_delivery(
    delivery_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[NotificationDeliveryPublic]:
    data = await NotificationService(session).retry_delivery(current_user.id, delivery_id)
    return ApiResponse(success=True, data=data, message="알림 delivery 재시도를 실행했습니다.")
