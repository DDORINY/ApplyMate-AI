from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError
from app.models.application import Application
from app.models.job import JobPosting
from app.models.schedule import (
    ScheduleConfidence,
    ScheduleEvent,
    ScheduleEventHistory,
    ScheduleEventStatus,
    ScheduleEventType,
    ScheduleHistoryAction,
    ScheduleHistorySource,
    ScheduleReminder,
    ScheduleReminderStatus,
    ScheduleReminderType,
)
from app.repositories.schedule import ScheduleRepository
from app.schemas.application import ApplicationOptionItem
from app.schemas.schedule import (
    ScheduleConflictItem,
    ScheduleEventCreate,
    ScheduleEventHistoryPublic,
    ScheduleEventListData,
    ScheduleEventPublic,
    ScheduleEventUpdate,
    ScheduleOptionsData,
    ScheduleReminderCreate,
    ScheduleReminderPublic,
    ScheduleReminderUpdate,
    ScheduleStatusChange,
    ScheduleUpcomingData,
    reminder_scheduled_at,
)


class ScheduleService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ScheduleRepository(session)

    async def create_event(self, user_id: int, payload: ScheduleEventCreate) -> ScheduleEventPublic:
        links = await self._validate_links(user_id, payload.application_id, payload.job_id)
        event = ScheduleEvent(
            user_id=user_id,
            application_id=links["application_id"],
            job_id=links["job_id"],
            title=payload.title,
            description=payload.description,
            event_type=payload.event_type,
            status=payload.status,
            confidence=payload.confidence,
            start_at=payload.start_at,
            end_at=payload.end_at,
            all_day=payload.all_day,
            timezone=payload.timezone,
            location=payload.location,
            online_url=payload.online_url,
            source=payload.source,
            source_reference=payload.source_reference,
            confirmation_required=payload.confirmation_required,
        )
        self.session.add(event)
        await self.session.flush()
        self._add_history(
            event,
            user_id,
            ScheduleHistoryAction.CREATED,
            previous_values=None,
            new_values=self._event_snapshot(event),
            changed_fields=list(self._event_snapshot(event).keys()),
        )
        for reminder_payload in payload.reminders:
            await self._create_reminder_model(user_id, event, reminder_payload, add_history=False)
        await self.session.commit()
        return await self.get_event(user_id, event.id)

    async def list_events(self, user_id: int, **filters) -> ScheduleEventListData:
        page = filters.pop("page")
        size = filters.pop("size")
        for field in ("start_from", "start_to"):
            if filters.get(field) is not None:
                filters[field] = self._require_aware(filters[field])
        events, total = await self.repository.list_events(user_id, page=page, size=size, **filters)
        total_pages = (total + size - 1) // size if total else 0
        return ScheduleEventListData(
            items=[await self._to_public(event) for event in events],
            page=page,
            size=size,
            total=total,
            total_pages=total_pages,
        )

    async def get_event(self, user_id: int, event_id: int) -> ScheduleEventPublic:
        event = await self._get_event_or_404(user_id, event_id)
        return await self._to_public(event)

    async def update_event(self, user_id: int, event_id: int, payload: ScheduleEventUpdate) -> ScheduleEventPublic:
        event = await self._get_event_or_404(user_id, event_id)
        data = payload.model_dump(exclude_unset=True)
        next_application_id = data.get("application_id", event.application_id)
        next_job_id = data.get("job_id", event.job_id)
        links = await self._validate_links(user_id, next_application_id, next_job_id)
        next_start = data.get("start_at", event.start_at)
        next_end = data.get("end_at", event.end_at)
        if next_start >= next_end:
            raise AppError("SCHEDULE_EVENT_INVALID_TIME_RANGE", "Schedule start time must be before end time.", 400)
        before = self._event_snapshot(event)
        for field, value in data.items():
            setattr(event, field, value)
        event.application_id = links["application_id"]
        event.job_id = links["job_id"]
        if event.status not in {ScheduleEventStatus.COMPLETED, ScheduleEventStatus.CANCELLED}:
            event.completed_at = None
            event.cancelled_at = None
        self._sync_reminder_times(event)
        after = self._event_snapshot(event)
        changed = [field for field, value in before.items() if after.get(field) != value]
        if changed:
            self._add_history(event, user_id, ScheduleHistoryAction.UPDATED, before, after, changed)
        await self.session.commit()
        return await self.get_event(user_id, event_id)

    async def archive_event(self, user_id: int, event_id: int) -> dict[str, bool]:
        event = await self._get_event_or_404(user_id, event_id)
        before = self._event_snapshot(event)
        event.is_archived = True
        self._add_history(
            event,
            user_id,
            ScheduleHistoryAction.ARCHIVED,
            before,
            {**before, "is_archived": True},
            ["is_archived"],
        )
        await self.session.commit()
        return {"archived": True}

    async def change_status(self, user_id: int, event_id: int, payload: ScheduleStatusChange) -> ScheduleEventPublic:
        event = await self._get_event_or_404(user_id, event_id, include_archived=True)
        if event.status == ScheduleEventStatus.CANCELLED and payload.status == ScheduleEventStatus.CANCELLED:
            raise AppError("SCHEDULE_EVENT_ALREADY_CANCELLED", "Schedule event is already cancelled.", 400)
        if event.status == ScheduleEventStatus.COMPLETED and payload.status == ScheduleEventStatus.COMPLETED:
            raise AppError("SCHEDULE_EVENT_ALREADY_COMPLETED", "Schedule event is already completed.", 400)
        before = self._event_snapshot(event)
        now = datetime.now(UTC)
        event.status = payload.status
        if payload.status == ScheduleEventStatus.COMPLETED:
            event.completed_at = now
            event.cancelled_at = None
            self._deactivate_reminders(event)
            action = ScheduleHistoryAction.COMPLETED
        elif payload.status == ScheduleEventStatus.CANCELLED:
            event.cancelled_at = now
            event.completed_at = None
            self._deactivate_reminders(event)
            action = ScheduleHistoryAction.CANCELLED
        else:
            event.completed_at = None
            event.cancelled_at = None
            action = ScheduleHistoryAction.STATUS_CHANGED
            for reminder in event.reminders:
                if reminder.status == ScheduleReminderStatus.INACTIVE:
                    reminder.status = ScheduleReminderStatus.ACTIVE
        after = self._event_snapshot(event)
        self._add_history(event, user_id, action, before, after, ["status", "completed_at", "cancelled_at"], payload.source)
        await self.session.commit()
        return await self.get_event(user_id, event_id)

    async def list_history(self, user_id: int, event_id: int) -> list[ScheduleEventHistoryPublic]:
        await self._get_event_or_404(user_id, event_id, include_archived=True)
        return [ScheduleEventHistoryPublic.model_validate(item) for item in await self.repository.list_history(user_id, event_id)]

    async def create_reminder(self, user_id: int, event_id: int, payload: ScheduleReminderCreate) -> ScheduleReminderPublic:
        event = await self._get_event_or_404(user_id, event_id, include_archived=True)
        reminder = await self._create_reminder_model(user_id, event, payload, add_history=True)
        await self.session.commit()
        await self.session.refresh(reminder)
        return ScheduleReminderPublic.model_validate(reminder)

    async def list_reminders(self, user_id: int, event_id: int) -> list[ScheduleReminderPublic]:
        await self._get_event_or_404(user_id, event_id, include_archived=True)
        reminders = await self.repository.list_reminders(user_id, event_id)
        return [ScheduleReminderPublic.model_validate(item) for item in reminders]

    async def update_reminder(
        self, user_id: int, event_id: int, reminder_id: int, payload: ScheduleReminderUpdate
    ) -> ScheduleReminderPublic:
        event = await self._get_event_or_404(user_id, event_id, include_archived=True)
        reminder = await self.repository.get_reminder(user_id, event_id, reminder_id)
        if not reminder:
            raise AppError("SCHEDULE_REMINDER_NOT_FOUND", "Schedule reminder was not found.", 404)
        data = payload.model_dump(exclude_unset=True)
        next_type = data.get("reminder_type", reminder.reminder_type)
        next_minutes = data.get("minutes_before", reminder.minutes_before)
        await self._validate_reminder(user_id, event, next_type, next_minutes, exclude_reminder_id=reminder.id)
        before = self._reminder_snapshot(reminder)
        for field, value in data.items():
            setattr(reminder, field, value)
        reminder.scheduled_at = reminder_scheduled_at(self._as_utc(event.start_at), reminder.minutes_before)
        after = self._reminder_snapshot(reminder)
        self._add_history(event, user_id, ScheduleHistoryAction.REMINDER_CHANGED, before, after, list(data.keys()))
        await self.session.commit()
        await self.session.refresh(reminder)
        return ScheduleReminderPublic.model_validate(reminder)

    async def delete_reminder(self, user_id: int, event_id: int, reminder_id: int) -> dict[str, bool]:
        event = await self._get_event_or_404(user_id, event_id, include_archived=True)
        reminder = await self.repository.get_reminder(user_id, event_id, reminder_id)
        if not reminder:
            raise AppError("SCHEDULE_REMINDER_NOT_FOUND", "Schedule reminder was not found.", 404)
        before = self._reminder_snapshot(reminder)
        await self.session.delete(reminder)
        self._add_history(event, user_id, ScheduleHistoryAction.REMINDER_CHANGED, before, None, ["deleted"])
        await self.session.commit()
        return {"deleted": True}

    async def conflicts(
        self, user_id: int, start_at: datetime, end_at: datetime, exclude_event_id: int | None = None
    ) -> list[ScheduleConflictItem]:
        start_at = self._require_aware(start_at)
        end_at = self._require_aware(end_at)
        if start_at >= end_at:
            raise AppError("SCHEDULE_EVENT_INVALID_TIME_RANGE", "Schedule start time must be before end time.", 400)
        conflicts = await self.repository.find_conflicts(user_id, start_at, end_at, exclude_event_id=exclude_event_id)
        return [self._to_conflict_item(event) for event in conflicts]

    async def upcoming(self, user_id: int, *, hours: int = 168, size: int = 20) -> ScheduleUpcomingData:
        now = datetime.now(UTC)
        data = await self.list_events(
            user_id,
            page=1,
            size=size,
            start_from=now,
            start_to=now + timedelta(hours=hours),
            include_archived=False,
            sort="start_at",
            order="asc",
        )
        return ScheduleUpcomingData(items=data.items)

    async def options(self, user_id: int) -> ScheduleOptionsData:
        applications = (
            await self.session.execute(
                select(Application).where(Application.user_id == user_id, Application.is_archived.is_(False)).order_by(Application.updated_at.desc())
            )
        ).scalars().all()
        jobs = (
            await self.session.execute(
                select(JobPosting).options(selectinload(JobPosting.company)).where(JobPosting.user_id == user_id).order_by(JobPosting.updated_at.desc())
            )
        ).scalars().all()
        return ScheduleOptionsData(
            event_types=[item.value for item in ScheduleEventType],
            statuses=[item.value for item in ScheduleEventStatus],
            confidences=[item.value for item in ScheduleConfidence],
            reminder_types=[item.value for item in ScheduleReminderType],
            reminder_presets=[10, 30, 60, 180, 1440, 4320, 10080],
            applications=[
                ApplicationOptionItem(
                    id=item.id,
                    label=f"{item.company_name_snapshot or '지원 항목'} · {item.job_title_snapshot or item.status.value}",
                    description=item.status.value,
                    metadata={"job_id": item.job_id, "priority": item.priority.value},
                )
                for item in applications
            ],
            jobs=[
                ApplicationOptionItem(
                    id=job.id,
                    label=f"{job.company.name if job.company else 'Unknown'} · {job.title}",
                    description=job.position or job.source_url,
                    metadata={"company_name": job.company.name if job.company else None, "deadline_at": job.deadline_at.isoformat() if job.deadline_at else None},
                )
                for job in jobs
            ],
        )

    async def _create_reminder_model(
        self, user_id: int, event: ScheduleEvent, payload: ScheduleReminderCreate, *, add_history: bool
    ) -> ScheduleReminder:
        await self._validate_reminder(user_id, event, payload.reminder_type, payload.minutes_before)
        status = (
            ScheduleReminderStatus.INACTIVE
            if event.status in {ScheduleEventStatus.CANCELLED, ScheduleEventStatus.COMPLETED}
            else ScheduleReminderStatus.ACTIVE
        )
        reminder = ScheduleReminder(
            event_id=event.id,
            user_id=user_id,
            reminder_type=payload.reminder_type,
            minutes_before=payload.minutes_before,
            scheduled_at=reminder_scheduled_at(self._as_utc(event.start_at), payload.minutes_before),
            status=status,
        )
        self.session.add(reminder)
        await self.session.flush()
        if add_history:
            self._add_history(
                event,
                user_id,
                ScheduleHistoryAction.REMINDER_CHANGED,
                None,
                self._reminder_snapshot(reminder),
                ["reminder"],
            )
        return reminder

    async def _validate_reminder(
        self,
        user_id: int,
        event: ScheduleEvent,
        reminder_type,
        minutes_before: int,
        *,
        exclude_reminder_id: int | None = None,
    ) -> None:
        scheduled_at = reminder_scheduled_at(self._as_utc(event.start_at), minutes_before)
        if scheduled_at >= self._as_utc(event.start_at):
            raise AppError("SCHEDULE_REMINDER_INVALID_TIME", "Reminder must be before schedule start time.", 400)
        duplicate = await self.repository.get_duplicate_reminder(
            user_id, event.id, reminder_type, minutes_before, exclude_reminder_id=exclude_reminder_id
        )
        if duplicate:
            raise AppError("SCHEDULE_REMINDER_DUPLICATE", "Duplicate reminder already exists.", 409)

    async def _get_event_or_404(self, user_id: int, event_id: int, *, include_archived: bool = False) -> ScheduleEvent:
        event = await self.repository.get_event(user_id, event_id, include_archived=include_archived)
        if not event:
            raise AppError("SCHEDULE_EVENT_NOT_FOUND", "Schedule event was not found.", 404)
        return event

    async def _validate_links(self, user_id: int, application_id: int | None, job_id: int | None) -> dict[str, int | None]:
        application = None
        if application_id:
            application = await self.session.scalar(
                select(Application).where(
                    Application.id == application_id,
                    Application.user_id == user_id,
                    Application.is_archived.is_(False),
                )
            )
            if not application:
                raise AppError("SCHEDULE_EVENT_APPLICATION_NOT_FOUND", "Linked application was not found.", 404)
        if job_id:
            job = await self.session.scalar(select(JobPosting).where(JobPosting.id == job_id, JobPosting.user_id == user_id))
            if not job:
                raise AppError("SCHEDULE_EVENT_JOB_NOT_FOUND", "Linked job posting was not found.", 404)
        if application and job_id and application.job_id and application.job_id != job_id:
            raise AppError("SCHEDULE_EVENT_RELATION_INVALID", "Application and job relation is invalid.", 400)
        if application and application.job_id and not job_id:
            job_id = application.job_id
        return {"application_id": application_id, "job_id": job_id}

    async def _to_public(self, event: ScheduleEvent) -> ScheduleEventPublic:
        conflicts = await self.repository.find_conflicts(event.user_id, self._as_utc(event.start_at), self._as_utc(event.end_at), exclude_event_id=event.id)
        now = datetime.now(UTC)
        start_at = self._as_utc(event.start_at)
        end_at = self._as_utc(event.end_at)
        active = event.status not in {ScheduleEventStatus.COMPLETED, ScheduleEventStatus.CANCELLED}
        is_overdue = active and end_at < now
        is_due_soon = active and not is_overdue and start_at <= now + timedelta(days=7)
        remaining_seconds = int((start_at - now).total_seconds()) if active else None
        effective_status = ScheduleEventStatus.MISSED if is_overdue and event.status in {ScheduleEventStatus.SCHEDULED, ScheduleEventStatus.CONFIRMED, ScheduleEventStatus.TENTATIVE} else event.status
        return ScheduleEventPublic(
            id=event.id,
            user_id=event.user_id,
            application_id=event.application_id,
            job_id=event.job_id,
            title=event.title,
            description=event.description,
            event_type=event.event_type,
            status=event.status,
            effective_status=effective_status,
            confidence=event.confidence,
            start_at=start_at,
            end_at=end_at,
            all_day=event.all_day,
            timezone=event.timezone,
            location=event.location,
            online_url=event.online_url,
            source=event.source,
            source_reference=event.source_reference,
            is_archived=event.is_archived,
            completed_at=self._as_utc(event.completed_at) if event.completed_at else None,
            cancelled_at=self._as_utc(event.cancelled_at) if event.cancelled_at else None,
            confirmation_required=event.confirmation_required,
            reminders_count=len(event.reminders or []),
            has_conflict=bool(conflicts),
            conflicting_events=[self._to_conflict_item(item) for item in conflicts],
            is_overdue=is_overdue,
            is_due_soon=is_due_soon,
            days_remaining=remaining_seconds // 86400 if remaining_seconds is not None else None,
            hours_remaining=remaining_seconds // 3600 if remaining_seconds is not None else None,
            created_at=self._as_utc(event.created_at),
            updated_at=self._as_utc(event.updated_at),
        )

    def _to_conflict_item(self, event: ScheduleEvent) -> ScheduleConflictItem:
        return ScheduleConflictItem(
            id=event.id,
            title=event.title,
            event_type=event.event_type,
            status=event.status,
            start_at=self._as_utc(event.start_at),
            end_at=self._as_utc(event.end_at),
        )

    def _sync_reminder_times(self, event: ScheduleEvent) -> None:
        for reminder in event.reminders:
            reminder.scheduled_at = reminder_scheduled_at(self._as_utc(event.start_at), reminder.minutes_before)
            if reminder.scheduled_at >= self._as_utc(event.start_at):
                raise AppError("SCHEDULE_REMINDER_INVALID_TIME", "Reminder must be before schedule start time.", 400)

    def _deactivate_reminders(self, event: ScheduleEvent) -> None:
        for reminder in event.reminders:
            if reminder.status == ScheduleReminderStatus.ACTIVE:
                reminder.status = ScheduleReminderStatus.INACTIVE

    def _add_history(
        self,
        event: ScheduleEvent,
        user_id: int,
        action: ScheduleHistoryAction,
        previous_values: dict | None,
        new_values: dict | None,
        changed_fields: list[str],
        source: ScheduleHistorySource = ScheduleHistorySource.USER,
    ) -> None:
        self.session.add(
            ScheduleEventHistory(
                event_id=event.id,
                user_id=user_id,
                action=action,
                previous_values=previous_values,
                new_values=new_values,
                changed_fields=changed_fields,
                source=source,
            )
        )

    def _event_snapshot(self, event: ScheduleEvent) -> dict:
        return {
            "application_id": event.application_id,
            "job_id": event.job_id,
            "title": event.title,
            "description": event.description,
            "event_type": event.event_type.value,
            "status": event.status.value,
            "confidence": event.confidence.value,
            "start_at": self._as_utc(event.start_at).isoformat(),
            "end_at": self._as_utc(event.end_at).isoformat(),
            "all_day": event.all_day,
            "timezone": event.timezone,
            "location": event.location,
            "online_url": event.online_url,
            "source": event.source,
            "source_reference": event.source_reference,
            "is_archived": event.is_archived,
            "completed_at": self._as_utc(event.completed_at).isoformat() if event.completed_at else None,
            "cancelled_at": self._as_utc(event.cancelled_at).isoformat() if event.cancelled_at else None,
            "confirmation_required": event.confirmation_required,
        }

    def _reminder_snapshot(self, reminder: ScheduleReminder) -> dict:
        return {
            "id": reminder.id,
            "reminder_type": reminder.reminder_type.value,
            "minutes_before": reminder.minutes_before,
            "scheduled_at": self._as_utc(reminder.scheduled_at).isoformat(),
            "status": reminder.status.value,
        }

    def _as_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    def _require_aware(self, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise AppError("SCHEDULE_EVENT_INVALID_TIMEZONE", "Timezone-aware datetime is required.", 400)
        return value.astimezone(UTC)
