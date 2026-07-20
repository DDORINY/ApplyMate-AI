from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.document_improvement import DocumentImprovementRun, DocumentImprovementRunStatus
from app.models.email_analysis import EmailCandidate, EmailCandidateStatus, EmailSyncRun, EmailSyncRunStatus
from app.models.integration import SyncRun, SyncRunStatus
from app.models.job_recommendation_automation import RecommendationNotificationCandidate, RecommendationNotificationStatus
from app.models.notification import Notification, NotificationDelivery, NotificationSetting, NotificationStatus
from app.models.schedule import ScheduleEvent, ScheduleEventStatus, ScheduleReminder, ScheduleReminderStatus
from app.models.user import User


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_setting(self, user_id: int) -> NotificationSetting | None:
        return await self.session.scalar(select(NotificationSetting).where(NotificationSetting.user_id == user_id))

    async def list_notifications(
        self,
        user_id: int,
        page: int,
        size: int,
        status: NotificationStatus | None = None,
    ) -> tuple[list[Notification], int]:
        base = select(Notification).where(Notification.user_id == user_id)
        if status:
            base = base.where(Notification.status == status)
        total_result = await self.session.execute(select(func.count()).select_from(base.order_by(None).subquery()))
        result = await self.session.execute(base.order_by(Notification.created_at.desc(), Notification.id.desc()).offset((page - 1) * size).limit(size))
        return list(result.scalars().all()), int(total_result.scalar_one())

    async def unread_count(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Notification).where(Notification.user_id == user_id, Notification.status == NotificationStatus.UNREAD)
        )
        return int(result.scalar_one())

    async def get_notification(self, user_id: int, notification_id: int) -> Notification | None:
        return await self.session.scalar(select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id))

    async def get_by_deduplication_key(self, key: str) -> Notification | None:
        return await self.session.scalar(select(Notification).where(Notification.deduplication_key == key))

    async def list_deliveries(self, user_id: int, page: int, size: int) -> tuple[list[NotificationDelivery], int]:
        base = select(NotificationDelivery).where(NotificationDelivery.user_id == user_id)
        total_result = await self.session.execute(select(func.count()).select_from(base.order_by(None).subquery()))
        result = await self.session.execute(
            base.options(selectinload(NotificationDelivery.notification))
            .order_by(NotificationDelivery.created_at.desc(), NotificationDelivery.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().unique().all()), int(total_result.scalar_one())

    async def get_delivery(self, user_id: int, delivery_id: int) -> NotificationDelivery | None:
        return await self.session.scalar(
            select(NotificationDelivery)
            .options(selectinload(NotificationDelivery.notification))
            .where(NotificationDelivery.id == delivery_id, NotificationDelivery.user_id == user_id)
        )

    async def due_schedule_reminders(self, limit: int = 100) -> list[tuple[ScheduleReminder, ScheduleEvent]]:
        now = datetime.now(UTC)
        result = await self.session.execute(
            select(ScheduleReminder, ScheduleEvent)
            .join(ScheduleEvent, ScheduleEvent.id == ScheduleReminder.event_id)
            .where(
                ScheduleReminder.status == ScheduleReminderStatus.ACTIVE,
                ScheduleReminder.scheduled_at <= now,
                ScheduleEvent.status != ScheduleEventStatus.CANCELLED,
                ScheduleEvent.is_archived.is_(False),
            )
            .order_by(ScheduleReminder.scheduled_at.asc())
            .limit(limit)
        )
        return list(result.all())

    async def pending_recommendation_candidates(self, limit: int = 100) -> list[RecommendationNotificationCandidate]:
        result = await self.session.execute(
            select(RecommendationNotificationCandidate)
            .where(RecommendationNotificationCandidate.status == RecommendationNotificationStatus.PENDING)
            .order_by(RecommendationNotificationCandidate.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def new_gmail_candidates(self, limit: int = 100) -> list[EmailCandidate]:
        result = await self.session.execute(
            select(EmailCandidate)
            .where(EmailCandidate.status == EmailCandidateStatus.NEW)
            .order_by(EmailCandidate.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def completed_document_improvements(self, limit: int = 100) -> list[DocumentImprovementRun]:
        result = await self.session.execute(
            select(DocumentImprovementRun)
            .where(
                DocumentImprovementRun.status.in_(
                    [
                        DocumentImprovementRunStatus.COMPLETED,
                        DocumentImprovementRunStatus.REVIEW_REQUIRED,
                        DocumentImprovementRunStatus.APPLIED,
                        DocumentImprovementRunStatus.FAILED,
                    ]
                )
            )
            .order_by(DocumentImprovementRun.completed_at.desc().nullslast(), DocumentImprovementRun.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def failed_sync_runs(self, limit: int = 100) -> tuple[list[SyncRun], list[EmailSyncRun]]:
        calendar_result = await self.session.execute(
            select(SyncRun).where(SyncRun.status == SyncRunStatus.FAILED).order_by(SyncRun.created_at.desc()).limit(limit)
        )
        gmail_result = await self.session.execute(
            select(EmailSyncRun).where(EmailSyncRun.status.in_([EmailSyncRunStatus.FAILED, EmailSyncRunStatus.PARTIAL_FAILED])).order_by(EmailSyncRun.created_at.desc()).limit(limit)
        )
        return list(calendar_result.scalars().all()), list(gmail_result.scalars().all())

    async def get_user(self, user_id: int) -> User | None:
        return await self.session.scalar(select(User).where(User.id == user_id))
