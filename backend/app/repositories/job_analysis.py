from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import JobAnalysis, JobAnalysisRun, JobAnalysisStatus


class JobAnalysisRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_analysis(self, user_id: int, job_id: int) -> JobAnalysis | None:
        result = await self.session.execute(
            select(JobAnalysis).where(
                JobAnalysis.user_id == user_id,
                JobAnalysis.job_posting_id == job_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_processing_analysis(self, user_id: int, job_id: int) -> JobAnalysis | None:
        result = await self.session.execute(
            select(JobAnalysis).where(
                JobAnalysis.user_id == user_id,
                JobAnalysis.job_posting_id == job_id,
                JobAnalysis.status == JobAnalysisStatus.PROCESSING,
            )
        )
        return result.scalar_one_or_none()

    async def count_runs_since(self, user_id: int, since: datetime) -> int:
        result = await self.session.execute(
            select(func.count()).where(
                JobAnalysisRun.user_id == user_id,
                JobAnalysisRun.created_at >= since,
            )
        )
        return int(result.scalar_one())

    async def latest_run(self, user_id: int) -> JobAnalysisRun | None:
        result = await self.session.execute(
            select(JobAnalysisRun)
            .where(JobAnalysisRun.user_id == user_id)
            .order_by(JobAnalysisRun.created_at.desc(), JobAnalysisRun.id.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_runs(
        self, user_id: int, job_id: int, page: int, size: int
    ) -> tuple[list[JobAnalysisRun], int]:
        base = select(JobAnalysisRun).where(
            JobAnalysisRun.user_id == user_id,
            JobAnalysisRun.job_posting_id == job_id,
        )
        total_result = await self.session.execute(
            select(func.count()).select_from(base.order_by(None).subquery())
        )
        total = int(total_result.scalar_one())
        result = await self.session.execute(
            base.order_by(JobAnalysisRun.created_at.desc(), JobAnalysisRun.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().all()), total
