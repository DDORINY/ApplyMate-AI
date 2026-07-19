from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.models.application import Application, ApplicationStatus
from app.models.application_document import ApplicationDocument
from app.models.job import JobAnalysis, JobMatch, JobPosting
from app.models.resume import ResumeAnalysis, ResumeFile
from app.models.schedule import ScheduleEvent, ScheduleEventStatus
from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import (
    DashboardActivityItem,
    DashboardApplicationActivity,
    DashboardApplicationStatusCount,
    DashboardDeadlineItem,
    DashboardPeriod,
    DashboardPreparingApplication,
    DashboardRecentDocument,
    DashboardRecentJobAnalysis,
    DashboardRecentMatch,
    DashboardRecentResumeAnalysis,
    DashboardResponse,
    DashboardScheduleItem,
    DashboardSummary,
)


APPLICATION_STATUS_GROUPS: dict[str, tuple[str, list[ApplicationStatus]]] = {
    "PREPARING": ("Preparing", [ApplicationStatus.SAVED, ApplicationStatus.PREPARING]),
    "APPLIED": ("Applied", [ApplicationStatus.APPLIED]),
    "IN_PROGRESS": (
        "In progress",
        [ApplicationStatus.DOCUMENT_REVIEW, ApplicationStatus.CODING_TEST, ApplicationStatus.ASSIGNMENT],
    ),
    "INTERVIEW": ("Interview", [ApplicationStatus.INTERVIEW, ApplicationStatus.FINAL_INTERVIEW]),
    "OFFER": ("Offer", [ApplicationStatus.OFFER]),
    "REJECTED": ("Rejected", [ApplicationStatus.REJECTED]),
    "WITHDRAWN": ("Withdrawn", [ApplicationStatus.WITHDRAWN]),
    "CLOSED": ("Closed", [ApplicationStatus.CLOSED]),
}


class DashboardService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = DashboardRepository(session)

    async def get_dashboard(
        self,
        user_id: int,
        *,
        period: DashboardPeriod,
        start_date: date | None,
        end_date: date | None,
        timezone: str,
        recent_limit: int,
    ) -> DashboardResponse:
        tz = self._timezone(timezone)
        now_local = datetime.now(tz)
        now_utc = now_local.astimezone(UTC)
        period_start, period_end = self._period_range(period, start_date, end_date, now_local, tz)
        today_start, today_end = self._day_range(now_local.date(), tz)
        week_start, week_end = self._week_range(now_local.date(), tz)
        deadline_end = now_utc + timedelta(days=7)

        status_counts = await self.repository.application_status_counts(user_id)
        grouped_counts = self._group_status_counts(status_counts)
        total_applications = sum(item.count for item in grouped_counts)
        new_applications = await self.repository.count_new_applications(user_id, period_start, period_end)
        status_changes = await self.repository.count_status_changes(user_id, period_start, period_end)

        today_events = await self.repository.list_schedule_events(user_id, today_start, today_end, limit=recent_limit)
        week_events = await self.repository.list_schedule_events(user_id, week_start, week_end, limit=recent_limit)
        upcoming_deadline_events = await self.repository.list_schedule_events(
            user_id, now_utc, deadline_end, limit=recent_limit, deadline_only=True
        )
        due_soon_jobs = await self.repository.list_due_soon_jobs(user_id, now_utc, deadline_end, limit=recent_limit)
        preparing_applications = await self.repository.list_preparing_applications(user_id, limit=recent_limit)
        recent_job_analyses = await self.repository.recent_job_analyses(user_id, limit=recent_limit)
        recent_matches = await self.repository.recent_matches(user_id, limit=recent_limit)
        recent_resume_analyses = await self.repository.recent_resume_analyses(user_id, limit=recent_limit)
        recent_documents = await self.repository.recent_documents(user_id, limit=recent_limit)
        recent_applications = await self.repository.recent_applications(user_id, limit=recent_limit)

        today_items = [self._schedule_item(event, now_utc, today_events) for event in today_events]
        week_items = [self._schedule_item(event, now_utc, week_events) for event in week_events]
        deadline_items = [self._schedule_deadline_item(event, now_utc) for event in upcoming_deadline_events]
        due_job_items = [self._job_deadline_item(job, now_utc) for job in due_soon_jobs]

        group_by_name = {item.group: item for item in grouped_counts}

        return DashboardResponse(
            summary=DashboardSummary(
                total_applications=total_applications,
                preparing_applications=group_by_name["PREPARING"].count,
                in_progress_applications=group_by_name["IN_PROGRESS"].count,
                interview_applications=group_by_name["INTERVIEW"].count,
                offer_applications=group_by_name["OFFER"].count,
                rejected_applications=group_by_name["REJECTED"].count,
                withdrawn_applications=group_by_name["WITHDRAWN"].count,
                closed_applications=group_by_name["CLOSED"].count,
                week_events=len(week_items),
                upcoming_deadlines=len(deadline_items),
                due_soon_jobs=len(due_job_items),
            ),
            application_status_counts=grouped_counts,
            application_activity=DashboardApplicationActivity(
                new_applications=new_applications,
                status_changes=status_changes,
                period_start=period_start,
                period_end=period_end,
            ),
            today_events=today_items,
            week_events=week_items,
            upcoming_deadlines=deadline_items,
            due_soon_jobs=due_job_items,
            preparing_applications=[self._preparing_application(item, now_utc) for item in preparing_applications],
            recent_job_analyses=[self._job_analysis(item) for item in recent_job_analyses],
            recent_matches=[self._match(item) for item in recent_matches],
            recent_resume_analyses=[self._resume_analysis(item) for item in recent_resume_analyses],
            recent_documents=[self._document(item) for item in recent_documents],
            recent_activities=self._activities(
                recent_applications,
                today_events,
                recent_job_analyses,
                recent_matches,
                recent_resume_analyses,
                recent_documents,
                recent_limit,
            ),
            generated_at=datetime.now(UTC),
            timezone=timezone,
            period=period,
            period_start=period_start,
            period_end=period_end,
        )

    def _group_status_counts(self, counts: dict[str, int]) -> list[DashboardApplicationStatusCount]:
        total = sum(counts.values())
        items: list[DashboardApplicationStatusCount] = []
        for group, (label, statuses) in APPLICATION_STATUS_GROUPS.items():
            count = sum(counts.get(status.value, 0) for status in statuses)
            percentage = round((count / total) * 100, 1) if total else 0.0
            items.append(
                DashboardApplicationStatusCount(
                    group=group,
                    label=label,
                    count=count,
                    percentage=percentage,
                    statuses=[status.value for status in statuses],
                )
            )
        return items

    def _timezone(self, timezone: str) -> ZoneInfo:
        try:
            return ZoneInfo(timezone)
        except ZoneInfoNotFoundError as exc:
            raise AppError("DASHBOARD_INVALID_TIMEZONE", "Invalid dashboard timezone.", 400) from exc

    def _period_range(
        self,
        period: DashboardPeriod,
        start_date: date | None,
        end_date: date | None,
        now_local: datetime,
        tz: ZoneInfo,
    ) -> tuple[datetime | None, datetime | None]:
        if start_date or end_date:
            if not start_date or not end_date:
                raise AppError("DASHBOARD_INVALID_DATE_RANGE", "start_date and end_date must be provided together.", 400)
            if start_date > end_date:
                raise AppError("DASHBOARD_INVALID_DATE_RANGE", "start_date must be before or equal to end_date.", 400)
            return self._day_range(start_date, tz)[0], self._day_range(end_date, tz)[1]
        if period == "all":
            return None, None
        if period == "custom":
            raise AppError("DASHBOARD_INVALID_DATE_RANGE", "Custom period requires start_date and end_date.", 400)
        days_by_period = {"7d": 7, "30d": 30, "90d": 90}
        days = days_by_period.get(period)
        if days is None:
            raise AppError("DASHBOARD_INVALID_PERIOD", "Invalid dashboard period.", 400)
        end = now_local.astimezone(UTC)
        start = (now_local - timedelta(days=days)).astimezone(UTC)
        return start, end

    def _day_range(self, target: date, tz: ZoneInfo) -> tuple[datetime, datetime]:
        start = datetime.combine(target, time.min, tzinfo=tz)
        end = start + timedelta(days=1)
        return start.astimezone(UTC), end.astimezone(UTC)

    def _week_range(self, target: date, tz: ZoneInfo) -> tuple[datetime, datetime]:
        start_date = target - timedelta(days=target.weekday())
        start = datetime.combine(start_date, time.min, tzinfo=tz)
        end = start + timedelta(days=7)
        return start.astimezone(UTC), end.astimezone(UTC)

    def _schedule_item(
        self, event: ScheduleEvent, now: datetime, range_events: list[ScheduleEvent]
    ) -> DashboardScheduleItem:
        start_at = self._as_utc(event.start_at)
        end_at = self._as_utc(event.end_at)
        is_overdue = end_at < now and event.status not in {ScheduleEventStatus.COMPLETED, ScheduleEventStatus.CANCELLED}
        effective_status = ScheduleEventStatus.MISSED.value if is_overdue else event.status.value
        return DashboardScheduleItem(
            id=event.id,
            title=event.title,
            event_type=event.event_type.value,
            status=event.status.value,
            effective_status=effective_status,
            confidence=event.confidence.value,
            start_at=start_at,
            end_at=end_at,
            all_day=event.all_day,
            timezone=event.timezone,
            application_id=event.application_id,
            job_id=event.job_id,
            company_name=getattr(event.application, "company_name_snapshot", None),
            job_title=getattr(event.application, "job_title_snapshot", None) or getattr(event.job, "title", None),
            location=event.location,
            online_url=event.online_url,
            has_conflict=self._has_conflict(event, range_events),
            hours_remaining=self._hours_between(now, start_at),
        )

    def _schedule_deadline_item(self, event: ScheduleEvent, now: datetime) -> DashboardDeadlineItem:
        due_at = self._as_utc(event.start_at)
        return DashboardDeadlineItem(
            kind="SCHEDULE",
            id=event.id,
            title=event.title,
            due_at=due_at,
            hours_remaining=self._hours_between(now, due_at),
            company_name=getattr(event.application, "company_name_snapshot", None),
            job_title=getattr(event.application, "job_title_snapshot", None) or getattr(event.job, "title", None),
            status=event.status.value,
            confidence=event.confidence.value,
            link_path=f"/calendar/events/{event.id}",
        )

    def _job_deadline_item(self, job: JobPosting, now: datetime) -> DashboardDeadlineItem:
        deadline_at = self._as_utc(job.deadline_at)
        return DashboardDeadlineItem(
            kind="JOB",
            id=job.id,
            title=job.title,
            due_at=deadline_at,
            hours_remaining=self._hours_between(now, deadline_at),
            company_name=job.company.name if job.company else None,
            job_title=job.title,
            status=job.status.value,
            confidence=job.deadline_type.value,
            link_path=f"/jobs/{job.id}",
        )

    def _preparing_application(self, application: Application, now: datetime) -> DashboardPreparingApplication:
        planned = self._as_utc(application.planned_apply_at) if application.planned_apply_at else None
        return DashboardPreparingApplication(
            id=application.id,
            company_name=application.company_name_snapshot,
            job_title=application.job_title_snapshot,
            status=application.status.value,
            priority=application.priority.value,
            planned_apply_at=planned,
            resume_id=application.resume_id,
            application_document_id=application.application_document_id,
            hours_until_planned_apply=self._hours_between(now, planned) if planned else None,
            link_path=f"/applications/{application.id}",
        )

    def _job_analysis(self, item: JobAnalysis) -> DashboardRecentJobAnalysis:
        job = item.job_posting
        skills = item.technical_skills if isinstance(item.technical_skills, list) else []
        return DashboardRecentJobAnalysis(
            id=item.id,
            job_id=item.job_posting_id,
            company_name=job.company.name if job and job.company else None,
            job_title=job.title if job else None,
            status=item.status.value,
            provider=None,
            summary=item.summary,
            technical_skills=[str(skill) for skill in skills[:5]],
            is_outdated=False,
            updated_at=self._as_utc(item.updated_at),
            link_path=f"/jobs/{item.job_posting_id}",
        )

    def _match(self, item: JobMatch) -> DashboardRecentMatch:
        job = item.job_posting
        return DashboardRecentMatch(
            id=item.id,
            job_id=item.job_posting_id,
            company_name=job.company.name if job and job.company else None,
            job_title=job.title if job else None,
            status=item.status.value,
            total_score=item.total_score,
            grade=item.grade.value,
            recommendation_status=item.recommendation_status.value,
            strengths=[str(value) for value in (item.strengths or [])[:3]],
            gaps=[str(value) for value in (item.gaps or [])[:3]],
            updated_at=self._as_utc(item.updated_at),
            link_path=f"/jobs/{item.job_posting_id}",
        )

    def _resume_analysis(self, item: ResumeAnalysis) -> DashboardRecentResumeAnalysis:
        resume_file: ResumeFile | None = item.resume_file
        result = item.result or {}
        skills = result.get("skills") if isinstance(result, dict) else []
        experiences = result.get("experiences") if isinstance(result, dict) else []
        return DashboardRecentResumeAnalysis(
            id=item.id,
            resume_id=item.resume_id,
            resume_file_id=item.resume_file_id,
            resume_title=None,
            filename=resume_file.original_filename if resume_file else None,
            status=item.status.value,
            provider=item.provider,
            summary=item.summary,
            skills_count=len(skills) if isinstance(skills, list) else 0,
            experiences_count=len(experiences) if isinstance(experiences, list) else 0,
            is_outdated=item.is_outdated,
            updated_at=self._as_utc(item.updated_at),
            link_path=f"/resumes/{item.resume_id}",
        )

    def _document(self, item: ApplicationDocument) -> DashboardRecentDocument:
        return DashboardRecentDocument(
            id=item.id,
            title=item.title,
            document_type=item.document_type.value,
            status=item.status.value,
            company_name=None,
            job_title=None,
            current_version_number=item.current_version_number,
            updated_at=self._as_utc(item.updated_at),
            link_path=f"/documents/{item.id}",
        )

    def _activities(
        self,
        applications: list[Application],
        schedules: list[ScheduleEvent],
        job_analyses: list[JobAnalysis],
        matches: list[JobMatch],
        resume_analyses: list[ResumeAnalysis],
        documents: list[ApplicationDocument],
        limit: int,
    ) -> list[DashboardActivityItem]:
        activities: list[DashboardActivityItem] = []
        for item in applications:
            activities.append(
                DashboardActivityItem(
                    id=f"application-{item.id}",
                    activity_type="APPLICATION_UPDATED",
                    title=item.job_title_snapshot or item.company_name_snapshot or "Application updated",
                    occurred_at=self._as_utc(item.updated_at),
                    link_path=f"/applications/{item.id}",
                    metadata={"status": item.status.value},
                )
            )
        for item in schedules:
            activities.append(
                DashboardActivityItem(
                    id=f"schedule-{item.id}",
                    activity_type="SCHEDULE_EVENT",
                    title=item.title,
                    occurred_at=self._as_utc(item.updated_at),
                    link_path=f"/calendar/events/{item.id}",
                    metadata={"status": item.status.value, "event_type": item.event_type.value},
                )
            )
        for item in job_analyses:
            activities.append(
                DashboardActivityItem(
                    id=f"job-analysis-{item.id}",
                    activity_type="JOB_ANALYSIS",
                    title=item.summary or f"Job analysis #{item.id}",
                    occurred_at=self._as_utc(item.updated_at),
                    link_path=f"/jobs/{item.job_posting_id}",
                    metadata={"status": item.status.value},
                )
            )
        for item in matches:
            activities.append(
                DashboardActivityItem(
                    id=f"job-match-{item.id}",
                    activity_type="JOB_MATCH",
                    title=f"Match {item.grade.value}",
                    occurred_at=self._as_utc(item.updated_at),
                    link_path=f"/jobs/{item.job_posting_id}",
                    metadata={"score": item.total_score},
                )
            )
        for item in resume_analyses:
            activities.append(
                DashboardActivityItem(
                    id=f"resume-analysis-{item.id}",
                    activity_type="RESUME_ANALYSIS",
                    title=item.summary or f"Resume analysis #{item.id}",
                    occurred_at=self._as_utc(item.updated_at),
                    link_path=f"/resumes/{item.resume_id}",
                    metadata={"status": item.status.value},
                )
            )
        for item in documents:
            activities.append(
                DashboardActivityItem(
                    id=f"document-{item.id}",
                    activity_type="APPLICATION_DOCUMENT",
                    title=item.title,
                    occurred_at=self._as_utc(item.updated_at),
                    link_path=f"/documents/{item.id}",
                    metadata={"status": item.status.value},
                )
            )
        return sorted(activities, key=lambda item: item.occurred_at, reverse=True)[:limit]

    def _has_conflict(self, event: ScheduleEvent, events: list[ScheduleEvent]) -> bool:
        start = self._as_utc(event.start_at)
        end = self._as_utc(event.end_at)
        return any(
            other.id != event.id
            and other.status != ScheduleEventStatus.CANCELLED
            and self._as_utc(other.start_at) < end
            and self._as_utc(other.end_at) > start
            for other in events
        )

    def _hours_between(self, start: datetime, end: datetime) -> int:
        return int((end - start).total_seconds() // 3600)

    def _as_utc(self, value: datetime | None) -> datetime:
        if value is None:
            raise ValueError("datetime value is required")
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
