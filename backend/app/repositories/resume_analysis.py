from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import ResumeAnalysis, ResumeAnalysisRun, ResumeAnalysisStatus


class ResumeAnalysisRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_analysis(self, user_id: int, resume_file_id: int) -> ResumeAnalysis | None:
        result = await self.session.execute(
            select(ResumeAnalysis).where(
                ResumeAnalysis.user_id == user_id,
                ResumeAnalysis.resume_file_id == resume_file_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_processing_analysis(self, user_id: int, resume_file_id: int) -> ResumeAnalysis | None:
        result = await self.session.execute(
            select(ResumeAnalysis).where(
                ResumeAnalysis.user_id == user_id,
                ResumeAnalysis.resume_file_id == resume_file_id,
                ResumeAnalysis.status == ResumeAnalysisStatus.PROCESSING,
            )
        )
        return result.scalar_one_or_none()

    async def list_runs(
        self, user_id: int, resume_file_id: int, page: int, size: int
    ) -> tuple[list[ResumeAnalysisRun], int]:
        base = select(ResumeAnalysisRun).where(
            ResumeAnalysisRun.user_id == user_id,
            ResumeAnalysisRun.resume_file_id == resume_file_id,
        )
        total_result = await self.session.execute(
            select(func.count()).select_from(base.order_by(None).subquery())
        )
        total = int(total_result.scalar_one())
        result = await self.session.execute(
            base.order_by(ResumeAnalysisRun.created_at.desc(), ResumeAnalysisRun.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().all()), total

    async def get_run(
        self, user_id: int, resume_file_id: int, run_id: int
    ) -> ResumeAnalysisRun | None:
        result = await self.session.execute(
            select(ResumeAnalysisRun).where(
                ResumeAnalysisRun.id == run_id,
                ResumeAnalysisRun.user_id == user_id,
                ResumeAnalysisRun.resume_file_id == resume_file_id,
            )
        )
        return result.scalar_one_or_none()
