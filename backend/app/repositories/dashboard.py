from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application, ApplicationStatus, ApplicationStatusHistory
from app.models.application_document import ApplicationDocument
from app.models.job import JobAnalysis, JobMatch, JobPosting
from app.models.resume import ResumeAnalysis
from app.models.schedule import ScheduleEvent, ScheduleEventStatus, ScheduleEventType


class DashboardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def application_status_counts(self, user_id: int) -> dict[str, int]:
        result = await self.session.execute(
            select(Application.status, func.count())
            .where(Application.user_id == user_id, Application.is_archived.is_(False))
            .group_by(Application.status)
        )
        return {status.value: int(count) for status, count in result.all()}

    async def count_new_applications(
        self, user_id: int, period_start: datetime | None, period_end: datetime | None
    ) -> int:
        query = select(func.count(Application.id)).where(
            Application.user_id == user_id,
            Application.is_archived.is_(False),
        )
        if period_start:
            query = query.where(Application.created_at >= period_start)
        if period_end:
            query = query.where(Application.created_at <= period_end)
        return int(await self.session.scalar(query) or 0)

    async def count_status_changes(
        self, user_id: int, period_start: datetime | None, period_end: datetime | None
    ) -> int:
        query = select(func.count(ApplicationStatusHistory.id)).where(ApplicationStatusHistory.user_id == user_id)
        if period_start:
            query = query.where(ApplicationStatusHistory.created_at >= period_start)
        if period_end:
            query = query.where(ApplicationStatusHistory.created_at <= period_end)
        return int(await self.session.scalar(query) or 0)

    async def list_schedule_events(
        self,
        user_id: int,
        start_at: datetime,
        end_at: datetime,
        *,
        limit: int = 20,
        deadline_only: bool = False,
    ) -> list[ScheduleEvent]:
        query = (
            select(ScheduleEvent)
            .options(selectinload(ScheduleEvent.application), selectinload(ScheduleEvent.job))
            .where(
                ScheduleEvent.user_id == user_id,
                ScheduleEvent.is_archived.is_(False),
                ScheduleEvent.status != ScheduleEventStatus.CANCELLED,
                ScheduleEvent.start_at < end_at,
                ScheduleEvent.end_at > start_at,
            )
        )
        if deadline_only:
            query = query.where(
                ScheduleEvent.event_type.in_(
                    [
                        ScheduleEventType.APPLICATION_DEADLINE,
                        ScheduleEventType.ASSIGNMENT_DEADLINE,
                        ScheduleEventType.OFFER_RESPONSE_DEADLINE,
                    ]
                )
            )
        result = await self.session.execute(query.order_by(ScheduleEvent.start_at.asc(), ScheduleEvent.id.asc()).limit(limit))
        return list(result.scalars().unique().all())

    async def list_due_soon_jobs(self, user_id: int, now: datetime, end_at: datetime, *, limit: int) -> list[JobPosting]:
        result = await self.session.execute(
            select(JobPosting)
            .options(selectinload(JobPosting.company), selectinload(JobPosting.match))
            .where(
                JobPosting.user_id == user_id,
                JobPosting.deadline_at.is_not(None),
                JobPosting.deadline_at >= now,
                JobPosting.deadline_at <= end_at,
            )
            .order_by(JobPosting.deadline_at.asc(), JobPosting.id.asc())
            .limit(limit)
        )
        return list(result.scalars().unique().all())

    async def list_preparing_applications(self, user_id: int, *, limit: int) -> list[Application]:
        result = await self.session.execute(
            select(Application)
            .where(
                Application.user_id == user_id,
                Application.is_archived.is_(False),
                Application.status.in_([ApplicationStatus.SAVED, ApplicationStatus.PREPARING]),
            )
            .order_by(
                Application.priority.desc(),
                Application.planned_apply_at.asc().nulls_last(),
                Application.updated_at.desc(),
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def recent_job_analyses(self, user_id: int, *, limit: int) -> list[JobAnalysis]:
        result = await self.session.execute(
            select(JobAnalysis)
            .options(selectinload(JobAnalysis.job_posting).selectinload(JobPosting.company))
            .where(JobAnalysis.user_id == user_id)
            .order_by(JobAnalysis.updated_at.desc(), JobAnalysis.id.desc())
            .limit(limit)
        )
        return list(result.scalars().unique().all())

    async def recent_matches(self, user_id: int, *, limit: int) -> list[JobMatch]:
        result = await self.session.execute(
            select(JobMatch)
            .options(selectinload(JobMatch.job_posting).selectinload(JobPosting.company))
            .where(JobMatch.user_id == user_id)
            .order_by(JobMatch.updated_at.desc(), JobMatch.id.desc())
            .limit(limit)
        )
        return list(result.scalars().unique().all())

    async def recent_resume_analyses(self, user_id: int, *, limit: int) -> list[ResumeAnalysis]:
        result = await self.session.execute(
            select(ResumeAnalysis)
            .options(
                selectinload(ResumeAnalysis.resume_file),
            )
            .where(ResumeAnalysis.user_id == user_id)
            .order_by(ResumeAnalysis.updated_at.desc(), ResumeAnalysis.id.desc())
            .limit(limit)
        )
        return list(result.scalars().unique().all())

    async def recent_documents(self, user_id: int, *, limit: int) -> list[ApplicationDocument]:
        result = await self.session.execute(
            select(ApplicationDocument)
            .where(ApplicationDocument.user_id == user_id, ApplicationDocument.is_archived.is_(False))
            .order_by(ApplicationDocument.updated_at.desc(), ApplicationDocument.id.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def recent_applications(self, user_id: int, *, limit: int) -> list[Application]:
        result = await self.session.execute(
            select(Application)
            .where(Application.user_id == user_id, Application.is_archived.is_(False))
            .order_by(Application.updated_at.desc(), Application.id.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
