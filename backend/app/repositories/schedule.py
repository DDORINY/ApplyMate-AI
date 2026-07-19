from datetime import datetime

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.schedule import (
    ScheduleConfidence,
    ScheduleEvent,
    ScheduleEventHistory,
    ScheduleEventStatus,
    ScheduleEventType,
    ScheduleReminder,
    ScheduleReminderType,
)


class ScheduleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_events(
        self,
        user_id: int,
        *,
        page: int,
        size: int,
        start_from: datetime | None = None,
        start_to: datetime | None = None,
        event_type: ScheduleEventType | None = None,
        status: ScheduleEventStatus | None = None,
        confidence: ScheduleConfidence | None = None,
        application_id: int | None = None,
        job_id: int | None = None,
        has_reminder: bool | None = None,
        include_archived: bool = False,
        keyword: str | None = None,
        sort: str = "start_at",
        order: str = "asc",
    ) -> tuple[list[ScheduleEvent], int]:
        query = select(ScheduleEvent).where(ScheduleEvent.user_id == user_id)
        query = self._apply_filters(
            query,
            start_from=start_from,
            start_to=start_to,
            event_type=event_type,
            status=status,
            confidence=confidence,
            application_id=application_id,
            job_id=job_id,
            has_reminder=has_reminder,
            include_archived=include_archived,
            keyword=keyword,
        )
        total_result = await self.session.execute(select(func.count()).select_from(query.order_by(None).subquery()))
        total = int(total_result.scalar_one())
        order_column = self._sort_column(sort)
        ordering = (order_column.desc(), ScheduleEvent.id.desc()) if order.lower() == "desc" else (order_column.asc(), ScheduleEvent.id.asc())
        result = await self.session.execute(
            query.options(selectinload(ScheduleEvent.reminders)).order_by(*ordering).offset((page - 1) * size).limit(size)
        )
        return list(result.scalars().unique().all()), total

    async def get_event(self, user_id: int, event_id: int, *, include_archived: bool = False) -> ScheduleEvent | None:
        query = (
            select(ScheduleEvent)
            .options(selectinload(ScheduleEvent.reminders), selectinload(ScheduleEvent.history))
            .where(ScheduleEvent.id == event_id, ScheduleEvent.user_id == user_id)
            .execution_options(populate_existing=True)
        )
        if not include_archived:
            query = query.where(ScheduleEvent.is_archived.is_(False))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_history(self, user_id: int, event_id: int) -> list[ScheduleEventHistory]:
        result = await self.session.execute(
            select(ScheduleEventHistory)
            .where(ScheduleEventHistory.user_id == user_id, ScheduleEventHistory.event_id == event_id)
            .order_by(ScheduleEventHistory.created_at.desc(), ScheduleEventHistory.id.desc())
        )
        return list(result.scalars().all())

    async def list_reminders(self, user_id: int, event_id: int) -> list[ScheduleReminder]:
        result = await self.session.execute(
            select(ScheduleReminder)
            .where(ScheduleReminder.user_id == user_id, ScheduleReminder.event_id == event_id)
            .order_by(ScheduleReminder.scheduled_at.asc(), ScheduleReminder.id.asc())
        )
        return list(result.scalars().all())

    async def get_reminder(self, user_id: int, event_id: int, reminder_id: int) -> ScheduleReminder | None:
        result = await self.session.execute(
            select(ScheduleReminder).where(
                ScheduleReminder.id == reminder_id,
                ScheduleReminder.user_id == user_id,
                ScheduleReminder.event_id == event_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_duplicate_reminder(
        self,
        user_id: int,
        event_id: int,
        reminder_type: ScheduleReminderType,
        minutes_before: int,
        *,
        exclude_reminder_id: int | None = None,
    ) -> ScheduleReminder | None:
        query = select(ScheduleReminder).where(
            ScheduleReminder.user_id == user_id,
            ScheduleReminder.event_id == event_id,
            ScheduleReminder.reminder_type == reminder_type,
            ScheduleReminder.minutes_before == minutes_before,
        )
        if exclude_reminder_id:
            query = query.where(ScheduleReminder.id != exclude_reminder_id)
        return await self.session.scalar(query)

    async def find_conflicts(
        self,
        user_id: int,
        start_at: datetime,
        end_at: datetime,
        *,
        exclude_event_id: int | None = None,
    ) -> list[ScheduleEvent]:
        query = select(ScheduleEvent).where(
            ScheduleEvent.user_id == user_id,
            ScheduleEvent.is_archived.is_(False),
            ScheduleEvent.status != ScheduleEventStatus.CANCELLED,
            ScheduleEvent.start_at < end_at,
            ScheduleEvent.end_at > start_at,
        )
        if exclude_event_id:
            query = query.where(ScheduleEvent.id != exclude_event_id)
        result = await self.session.execute(query.order_by(ScheduleEvent.start_at.asc(), ScheduleEvent.id.asc()))
        return list(result.scalars().all())

    def _apply_filters(
        self,
        query: Select[tuple[ScheduleEvent]],
        *,
        start_from: datetime | None,
        start_to: datetime | None,
        event_type: ScheduleEventType | None,
        status: ScheduleEventStatus | None,
        confidence: ScheduleConfidence | None,
        application_id: int | None,
        job_id: int | None,
        has_reminder: bool | None,
        include_archived: bool,
        keyword: str | None,
    ) -> Select[tuple[ScheduleEvent]]:
        if not include_archived:
            query = query.where(ScheduleEvent.is_archived.is_(False))
        if start_from:
            query = query.where(ScheduleEvent.end_at >= start_from)
        if start_to:
            query = query.where(ScheduleEvent.start_at <= start_to)
        if event_type:
            query = query.where(ScheduleEvent.event_type == event_type)
        if status:
            query = query.where(ScheduleEvent.status == status)
        if confidence:
            query = query.where(ScheduleEvent.confidence == confidence)
        if application_id:
            query = query.where(ScheduleEvent.application_id == application_id)
        if job_id:
            query = query.where(ScheduleEvent.job_id == job_id)
        if has_reminder is not None:
            reminder_exists = select(ScheduleReminder.id).where(ScheduleReminder.event_id == ScheduleEvent.id).exists()
            query = query.where(reminder_exists if has_reminder else ~reminder_exists)
        if keyword:
            pattern = f"%{keyword.lower()}%"
            query = query.where(
                or_(
                    func.lower(ScheduleEvent.title).like(pattern),
                    func.lower(ScheduleEvent.description).like(pattern),
                    func.lower(ScheduleEvent.location).like(pattern),
                    func.lower(ScheduleEvent.source).like(pattern),
                )
            )
        return query

    def _sort_column(self, sort: str):
        return {
            "start_at": ScheduleEvent.start_at,
            "end_at": ScheduleEvent.end_at,
            "created_at": ScheduleEvent.created_at,
            "updated_at": ScheduleEvent.updated_at,
            "status": ScheduleEvent.status,
            "event_type": ScheduleEvent.event_type,
        }.get(sort, ScheduleEvent.start_at)
