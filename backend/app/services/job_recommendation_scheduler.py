from datetime import timedelta
from math import ceil

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.security import utc_now
from app.models.job_recommendation_automation import (
    RecommendationNotificationStatus,
    RecommendationRunFrequency,
    RecommendationRunSkipReason,
)
from app.repositories.job_recommendation_automation import JobRecommendationAutomationRepository
from app.schemas.job_recommendation import JobRecommendationGenerateRequest
from app.schemas.job_recommendation_automation import (
    JobRecommendationRunIfDueData,
    JobRecommendationRunIfDueRequest,
    JobRecommendationSettingsPublic,
    JobRecommendationSettingsUpdate,
    RecommendationNotificationListData,
    RecommendationNotificationPublic,
    RecommendationNotificationUpdate,
)
from app.services.job_recommendation import JobRecommendationService
from app.services.job_recommendation_snapshot import JobRecommendationSnapshotService


class JobRecommendationSchedulerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = JobRecommendationAutomationRepository(session)

    async def get_settings(self, user_id: int) -> JobRecommendationSettingsPublic:
        setting = await self.repository.ensure_setting(user_id)
        await self.session.commit()
        await self.session.refresh(setting)
        return JobRecommendationSettingsPublic.model_validate(setting)

    async def update_settings(self, user_id: int, payload: JobRecommendationSettingsUpdate) -> JobRecommendationSettingsPublic:
        setting = await self.repository.ensure_setting(user_id)
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(setting, key, value)
        setting.next_run_at = self._calculate_next_run(setting.frequency) if setting.enabled else None
        await self.session.commit()
        await self.session.refresh(setting)
        return JobRecommendationSettingsPublic.model_validate(setting)

    async def run_if_due(self, user_id: int, payload: JobRecommendationRunIfDueRequest) -> JobRecommendationRunIfDueData:
        setting = await self.repository.ensure_setting(user_id)
        skip_reason = await self._skip_reason(user_id, setting, payload.force)
        if skip_reason:
            await self.session.commit()
            return JobRecommendationRunIfDueData(
                executed=False,
                skip_reason=skip_reason,
                next_run_at=setting.next_run_at,
                message=self._skip_message(skip_reason),
            )

        generated = await JobRecommendationService(self.session).generate(
            user_id,
            JobRecommendationGenerateRequest(
                force_refresh=True,
                include_jobs_without_analysis=setting.include_jobs_without_analysis,
                exclude_applied_jobs=setting.exclude_applied_jobs,
            ),
        )
        snapshot = await JobRecommendationSnapshotService(self.session).create_for_run(
            user_id,
            generated.run_id,
            minimum_score=setting.minimum_score,
        )
        setting = await self.repository.ensure_setting(user_id)
        setting.last_run_at = utc_now()
        setting.next_run_at = self._calculate_next_run(setting.frequency)
        await self.session.commit()
        return JobRecommendationRunIfDueData(
            executed=True,
            run_id=generated.run_id,
            snapshot_id=snapshot.id,
            recommended_count=snapshot.recommended_count,
            new_count=snapshot.new_count,
            changed_count=snapshot.changed_count,
            removed_count=snapshot.removed_count,
            next_run_at=setting.next_run_at,
            message="추천 실행과 Snapshot 생성이 완료되었습니다.",
        )

    async def _skip_reason(self, user_id: int, setting, force: bool) -> RecommendationRunSkipReason | None:
        if await self.repository.has_running_run(user_id):
            return RecommendationRunSkipReason.ALREADY_RUNNING
        if not await self.repository.has_profile(user_id):
            return RecommendationRunSkipReason.PROFILE_MISSING
        if await self.repository.active_job_count(user_id) == 0:
            return RecommendationRunSkipReason.NO_ACTIVE_JOBS
        if force:
            return None
        if not setting.enabled:
            return RecommendationRunSkipReason.DISABLED
        if setting.frequency == RecommendationRunFrequency.MANUAL:
            return RecommendationRunSkipReason.NOT_DUE
        if setting.next_run_at and setting.next_run_at > utc_now():
            return RecommendationRunSkipReason.NOT_DUE
        return None

    def _calculate_next_run(self, frequency: RecommendationRunFrequency):
        now = utc_now()
        if frequency == RecommendationRunFrequency.DAILY:
            return now + timedelta(days=1)
        if frequency == RecommendationRunFrequency.WEEKLY:
            return now + timedelta(days=7)
        return None

    def _skip_message(self, reason: RecommendationRunSkipReason) -> str:
        messages = {
            RecommendationRunSkipReason.DISABLED: "추천 자동 실행 설정이 꺼져 있습니다.",
            RecommendationRunSkipReason.NOT_DUE: "아직 추천 실행 시점이 아닙니다.",
            RecommendationRunSkipReason.PROFILE_MISSING: "추천 실행을 위해 커리어 프로필이 필요합니다.",
            RecommendationRunSkipReason.NO_ACTIVE_JOBS: "추천할 활성 채용공고가 없습니다.",
            RecommendationRunSkipReason.DUPLICATE_INPUT: "동일 입력으로 이미 추천이 생성되었습니다.",
            RecommendationRunSkipReason.ALREADY_RUNNING: "추천 실행이 이미 진행 중입니다.",
        }
        return messages[reason]

    async def list_notifications(
        self,
        user_id: int,
        *,
        page: int,
        size: int,
        status: RecommendationNotificationStatus | None,
    ) -> RecommendationNotificationListData:
        items, total = await self.repository.list_notifications(user_id, page=page, size=size, status=status)
        return RecommendationNotificationListData(
            items=[RecommendationNotificationPublic.model_validate(item) for item in items],
            page=page,
            size=size,
            total=total,
            total_pages=ceil(total / size) if total else 0,
        )

    async def update_notification(
        self,
        user_id: int,
        notification_id: int,
        payload: RecommendationNotificationUpdate,
    ) -> RecommendationNotificationPublic:
        notification = await self.repository.get_notification(user_id, notification_id)
        if not notification:
            raise AppError("RECOMMENDATION_NOTIFICATION_NOT_FOUND", "추천 알림 후보를 찾을 수 없습니다.", 404)
        if notification.status == RecommendationNotificationStatus.DISMISSED and payload.status == RecommendationNotificationStatus.DISMISSED:
            raise AppError("RECOMMENDATION_NOTIFICATION_ALREADY_DISMISSED", "이미 해제된 추천 알림 후보입니다.", 409)
        notification.status = payload.status
        if payload.status == RecommendationNotificationStatus.READ:
            notification.read_at = utc_now()
        if payload.status == RecommendationNotificationStatus.DISMISSED:
            notification.dismissed_at = utc_now()
        await self.session.commit()
        await self.session.refresh(notification)
        return RecommendationNotificationPublic.model_validate(notification)

    async def delete_notification(self, user_id: int, notification_id: int) -> dict[str, bool]:
        notification = await self.repository.get_notification(user_id, notification_id)
        if not notification:
            raise AppError("RECOMMENDATION_NOTIFICATION_NOT_FOUND", "추천 알림 후보를 찾을 수 없습니다.", 404)
        notification.status = RecommendationNotificationStatus.DISMISSED
        notification.dismissed_at = utc_now()
        await self.session.commit()
        return {"deleted": True}
