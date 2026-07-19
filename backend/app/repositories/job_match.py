from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import JobMatch, JobMatchFeedback, JobMatchRun, JobMatchStatus


class JobMatchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_match(self, user_id: int, job_id: int) -> JobMatch | None:
        result = await self.session.execute(
            select(JobMatch).where(JobMatch.user_id == user_id, JobMatch.job_posting_id == job_id)
        )
        return result.scalar_one_or_none()

    async def get_processing_match(self, user_id: int, job_id: int) -> JobMatch | None:
        result = await self.session.execute(
            select(JobMatch).where(
                JobMatch.user_id == user_id,
                JobMatch.job_posting_id == job_id,
                JobMatch.status == JobMatchStatus.PROCESSING,
            )
        )
        return result.scalar_one_or_none()

    async def list_runs(
        self, user_id: int, job_id: int, page: int, size: int, status: JobMatchStatus | None = None
    ) -> tuple[list[JobMatchRun], int]:
        base = select(JobMatchRun).where(
            JobMatchRun.user_id == user_id, JobMatchRun.job_posting_id == job_id
        )
        if status:
            base = base.where(JobMatchRun.status == status)
        total_result = await self.session.execute(
            select(func.count()).select_from(base.order_by(None).subquery())
        )
        total = int(total_result.scalar_one())
        result = await self.session.execute(
            base.order_by(JobMatchRun.created_at.desc(), JobMatchRun.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().all()), total

    async def list_feedback(self, user_id: int, job_match_id: int) -> list[JobMatchFeedback]:
        result = await self.session.execute(
            select(JobMatchFeedback)
            .where(JobMatchFeedback.user_id == user_id, JobMatchFeedback.job_match_id == job_match_id)
            .order_by(JobMatchFeedback.created_at.desc(), JobMatchFeedback.id.desc())
        )
        return list(result.scalars().all())

    async def get_feedback(self, user_id: int, feedback_id: int) -> JobMatchFeedback | None:
        result = await self.session.execute(
            select(JobMatchFeedback).where(
                JobMatchFeedback.id == feedback_id,
                JobMatchFeedback.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()
