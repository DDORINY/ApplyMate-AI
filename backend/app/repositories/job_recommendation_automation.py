from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.career import CareerProfile
from app.models.job import JobPosting, JobPostingStatus
from app.models.job_recommendation import JobRecommendation, JobRecommendationRun, JobRecommendationRunStatus
from app.models.job_recommendation_automation import (
    JobRecommendationSetting,
    JobRecommendationSnapshot,
    JobRecommendationSnapshotItem,
    RecommendationChangeType,
    RecommendationNotificationCandidate,
    RecommendationNotificationStatus,
)


class JobRecommendationAutomationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_setting(self, user_id: int) -> JobRecommendationSetting | None:
        return await self.session.scalar(select(JobRecommendationSetting).where(JobRecommendationSetting.user_id == user_id))

    async def ensure_setting(self, user_id: int) -> JobRecommendationSetting:
        setting = await self.get_setting(user_id)
        if setting:
            return setting
        setting = JobRecommendationSetting(user_id=user_id)
        self.session.add(setting)
        await self.session.flush()
        return setting

    async def has_profile(self, user_id: int) -> bool:
        profile_id = await self.session.scalar(select(CareerProfile.id).where(CareerProfile.user_id == user_id))
        return profile_id is not None

    async def active_job_count(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count(JobPosting.id)).where(
                JobPosting.user_id == user_id,
                JobPosting.status.in_([JobPostingStatus.SAVED, JobPostingStatus.REVIEWING, JobPostingStatus.INTERESTED]),
                or_(JobPosting.deadline_at.is_(None), JobPosting.deadline_at > func.now()),
            )
        )
        return int(result.scalar_one())

    async def has_running_run(self, user_id: int) -> bool:
        run_id = await self.session.scalar(
            select(JobRecommendationRun.id).where(
                JobRecommendationRun.user_id == user_id,
                JobRecommendationRun.status == JobRecommendationRunStatus.PROCESSING,
            )
        )
        return run_id is not None

    async def recommendations_for_run(self, user_id: int, run_id: int) -> list[JobRecommendation]:
        result = await self.session.execute(
            select(JobRecommendation)
            .options(selectinload(JobRecommendation.reasons), selectinload(JobRecommendation.feedback), selectinload(JobRecommendation.job))
            .where(JobRecommendation.user_id == user_id, JobRecommendation.run_id == run_id)
            .order_by(JobRecommendation.score.desc(), JobRecommendation.id.desc())
        )
        return list(result.scalars().unique().all())

    async def latest_snapshot(self, user_id: int, before_snapshot_id: int | None = None) -> JobRecommendationSnapshot | None:
        query = (
            select(JobRecommendationSnapshot)
            .options(selectinload(JobRecommendationSnapshot.items))
            .where(JobRecommendationSnapshot.user_id == user_id)
            .order_by(JobRecommendationSnapshot.generated_at.desc(), JobRecommendationSnapshot.id.desc())
        )
        if before_snapshot_id is not None:
            query = query.where(JobRecommendationSnapshot.id != before_snapshot_id)
        result = await self.session.execute(query.limit(1))
        return result.scalar_one_or_none()

    async def get_snapshot(self, user_id: int, snapshot_id: int) -> JobRecommendationSnapshot | None:
        result = await self.session.execute(
            select(JobRecommendationSnapshot)
            .options(selectinload(JobRecommendationSnapshot.items))
            .where(JobRecommendationSnapshot.id == snapshot_id, JobRecommendationSnapshot.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_snapshots(self, user_id: int, page: int, size: int) -> tuple[list[JobRecommendationSnapshot], int]:
        base = select(JobRecommendationSnapshot).where(JobRecommendationSnapshot.user_id == user_id)
        total_result = await self.session.execute(select(func.count()).select_from(base.order_by(None).subquery()))
        total = int(total_result.scalar_one())
        result = await self.session.execute(
            base.options(selectinload(JobRecommendationSnapshot.items))
            .order_by(JobRecommendationSnapshot.generated_at.desc(), JobRecommendationSnapshot.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().unique().all()), total

    async def list_changes(
        self,
        user_id: int,
        *,
        page: int,
        size: int,
        change_type: RecommendationChangeType | None = None,
    ) -> tuple[list[JobRecommendationSnapshotItem], int]:
        query = select(JobRecommendationSnapshotItem).join(JobRecommendationSnapshot).where(JobRecommendationSnapshot.user_id == user_id)
        if change_type:
            query = query.where(JobRecommendationSnapshotItem.change_type == change_type)
        total_result = await self.session.execute(select(func.count()).select_from(query.order_by(None).subquery()))
        total = int(total_result.scalar_one())
        result = await self.session.execute(
            query.order_by(JobRecommendationSnapshotItem.created_at.desc(), JobRecommendationSnapshotItem.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().all()), total

    async def latest_item_for_recommendation(self, user_id: int, recommendation_id: int) -> JobRecommendationSnapshotItem | None:
        result = await self.session.execute(
            select(JobRecommendationSnapshotItem)
            .join(JobRecommendationSnapshot)
            .where(
                JobRecommendationSnapshot.user_id == user_id,
                JobRecommendationSnapshotItem.recommendation_id == recommendation_id,
            )
            .order_by(JobRecommendationSnapshot.generated_at.desc(), JobRecommendationSnapshotItem.id.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_notifications(
        self,
        user_id: int,
        *,
        page: int,
        size: int,
        status: RecommendationNotificationStatus | None = None,
    ) -> tuple[list[RecommendationNotificationCandidate], int]:
        query = select(RecommendationNotificationCandidate).where(RecommendationNotificationCandidate.user_id == user_id)
        if status:
            query = query.where(RecommendationNotificationCandidate.status == status)
        total_result = await self.session.execute(select(func.count()).select_from(query.order_by(None).subquery()))
        total = int(total_result.scalar_one())
        result = await self.session.execute(
            query.order_by(RecommendationNotificationCandidate.created_at.desc(), RecommendationNotificationCandidate.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().all()), total

    async def get_notification(self, user_id: int, notification_id: int) -> RecommendationNotificationCandidate | None:
        return await self.session.scalar(
            select(RecommendationNotificationCandidate).where(
                RecommendationNotificationCandidate.id == notification_id,
                RecommendationNotificationCandidate.user_id == user_id,
            )
        )

    async def notification_exists(
        self,
        user_id: int,
        snapshot_id: int,
        recommendation_id: int | None,
        notification_type: str,
    ) -> bool:
        existing_id = await self.session.scalar(
            select(RecommendationNotificationCandidate.id).where(
                RecommendationNotificationCandidate.user_id == user_id,
                RecommendationNotificationCandidate.snapshot_id == snapshot_id,
                RecommendationNotificationCandidate.recommendation_id == recommendation_id,
                RecommendationNotificationCandidate.notification_type == notification_type,
            )
        )
        return existing_id is not None

    async def hidden_or_applied_job_ids(self, user_id: int) -> set[int]:
        from app.models.job_recommendation import JobRecommendationFeedback, JobRecommendationFeedbackType

        result = await self.session.execute(
            select(JobRecommendation.job_id)
            .join(JobRecommendationFeedback, JobRecommendationFeedback.recommendation_id == JobRecommendation.id)
            .where(
                JobRecommendation.user_id == user_id,
                JobRecommendationFeedback.user_id == user_id,
                JobRecommendationFeedback.feedback_type.in_(
                    [
                        JobRecommendationFeedbackType.HIDDEN,
                        JobRecommendationFeedbackType.NOT_INTERESTED,
                        JobRecommendationFeedbackType.APPLIED,
                    ]
                ),
            )
        )
        return {int(row[0]) for row in result.all()}
