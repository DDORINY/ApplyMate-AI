from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_session
from app.models.job_recommendation_automation import RecommendationChangeType, RecommendationNotificationStatus
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.job_recommendation_automation import (
    JobRecommendationChangeListData,
    JobRecommendationRunIfDueData,
    JobRecommendationRunIfDueRequest,
    JobRecommendationSettingsPublic,
    JobRecommendationSettingsUpdate,
    JobRecommendationSnapshotListData,
    JobRecommendationSnapshotPublic,
    RecommendationNotificationListData,
    RecommendationNotificationPublic,
    RecommendationNotificationUpdate,
)
from app.services.job_recommendation_scheduler import JobRecommendationSchedulerService
from app.services.job_recommendation_snapshot import JobRecommendationSnapshotService

router = APIRouter(tags=["job-recommendation-automation"])


@router.get("/recommendations/settings", response_model=ApiResponse[JobRecommendationSettingsPublic])
async def get_recommendation_settings(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobRecommendationSettingsPublic]:
    data = await JobRecommendationSchedulerService(session).get_settings(current_user.id)
    return ApiResponse(success=True, data=data, message="추천 실행 설정입니다.")


@router.patch("/recommendations/settings", response_model=ApiResponse[JobRecommendationSettingsPublic])
async def update_recommendation_settings(
    payload: JobRecommendationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobRecommendationSettingsPublic]:
    data = await JobRecommendationSchedulerService(session).update_settings(current_user.id, payload)
    return ApiResponse(success=True, data=data, message="추천 실행 설정이 저장되었습니다.")


@router.post("/recommendations/jobs/run-if-due", response_model=ApiResponse[JobRecommendationRunIfDueData])
async def run_job_recommendations_if_due(
    payload: JobRecommendationRunIfDueRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobRecommendationRunIfDueData]:
    data = await JobRecommendationSchedulerService(session).run_if_due(current_user.id, payload)
    return ApiResponse(success=True, data=data, message=data.message)


@router.get("/recommendations/jobs/snapshots", response_model=ApiResponse[JobRecommendationSnapshotListData])
async def list_job_recommendation_snapshots(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[JobRecommendationSnapshotListData]:
    data = await JobRecommendationSnapshotService(session).list_snapshots(current_user.id, page, size)
    return ApiResponse(success=True, data=data, message="추천 Snapshot 목록입니다.")


@router.get("/recommendations/jobs/snapshots/{snapshot_id}", response_model=ApiResponse[JobRecommendationSnapshotPublic])
async def get_job_recommendation_snapshot(
    snapshot_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobRecommendationSnapshotPublic]:
    data = await JobRecommendationSnapshotService(session).get_snapshot(current_user.id, snapshot_id)
    return ApiResponse(success=True, data=data, message="추천 Snapshot 상세입니다.")


@router.get("/recommendations/jobs/changes", response_model=ApiResponse[JobRecommendationChangeListData])
async def list_job_recommendation_changes(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    change_type: RecommendationChangeType | None = None,
) -> ApiResponse[JobRecommendationChangeListData]:
    data = await JobRecommendationSnapshotService(session).list_changes(
        current_user.id,
        page=page,
        size=size,
        change_type=change_type,
    )
    return ApiResponse(success=True, data=data, message="추천 변화 목록입니다.")


@router.get("/recommendation-notifications", response_model=ApiResponse[RecommendationNotificationListData])
async def list_recommendation_notifications(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status: RecommendationNotificationStatus | None = None,
) -> ApiResponse[RecommendationNotificationListData]:
    data = await JobRecommendationSchedulerService(session).list_notifications(current_user.id, page=page, size=size, status=status)
    return ApiResponse(success=True, data=data, message="추천 알림 후보 목록입니다.")


@router.patch("/recommendation-notifications/{notification_id}", response_model=ApiResponse[RecommendationNotificationPublic])
async def update_recommendation_notification(
    notification_id: int,
    payload: RecommendationNotificationUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[RecommendationNotificationPublic]:
    data = await JobRecommendationSchedulerService(session).update_notification(current_user.id, notification_id, payload)
    return ApiResponse(success=True, data=data, message="추천 알림 후보가 수정되었습니다.")


@router.delete("/recommendation-notifications/{notification_id}", response_model=ApiResponse[dict[str, bool]])
async def delete_recommendation_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, bool]]:
    data = await JobRecommendationSchedulerService(session).delete_notification(current_user.id, notification_id)
    return ApiResponse(success=True, data=data, message="추천 알림 후보가 해제되었습니다.")
