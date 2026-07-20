from datetime import UTC, datetime, timedelta
from math import ceil
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.models.document_improvement import DocumentImprovementRunStatus
from app.models.job_recommendation_automation import RecommendationNotificationStatus, RecommendationNotificationType
from app.models.notification import (
    Notification,
    NotificationChannel,
    NotificationDelivery,
    NotificationDeliveryStatus,
    NotificationEventType,
    NotificationPriority,
    NotificationProcessingRun,
    NotificationProcessingRunStatus,
    NotificationProcessingTaskType,
    NotificationSetting,
    NotificationStatus,
)
from app.models.schedule import ScheduleEventType, ScheduleReminderStatus
from app.notifications.providers import get_notification_email_provider
from app.repositories.notification import NotificationRepository
from app.schemas.notification import (
    NotificationDeliveryListData,
    NotificationDeliveryPublic,
    NotificationListData,
    NotificationProcessingRunPublic,
    NotificationPublic,
    NotificationSettingPublic,
    NotificationSettingUpdate,
    NotificationUnreadCountData,
)


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = NotificationRepository(session)

    async def get_or_create_setting(self, user_id: int) -> NotificationSetting:
        setting = await self.repository.get_setting(user_id)
        if setting:
            return setting
        setting = NotificationSetting(user_id=user_id)
        self.session.add(setting)
        await self.session.commit()
        await self.session.refresh(setting)
        return setting

    async def get_settings(self, user_id: int) -> NotificationSettingPublic:
        return NotificationSettingPublic.model_validate(await self.get_or_create_setting(user_id))

    async def update_settings(self, user_id: int, payload: NotificationSettingUpdate) -> NotificationSettingPublic:
        setting = await self.get_or_create_setting(user_id)
        values = payload.model_dump(exclude_unset=True)
        if "timezone" in values and values["timezone"]:
            try:
                ZoneInfo(values["timezone"])
            except ZoneInfoNotFoundError as exc:
                raise AppError("NOTIFICATION_SETTINGS_INVALID", "알림 timezone이 올바르지 않습니다.", 400) from exc
        for key, value in values.items():
            setattr(setting, key, value)
        await self.session.commit()
        await self.session.refresh(setting)
        return NotificationSettingPublic.model_validate(setting)

    async def list_notifications(
        self,
        user_id: int,
        page: int,
        size: int,
        status: NotificationStatus | None,
    ) -> NotificationListData:
        items, total = await self.repository.list_notifications(user_id, page, size, status)
        return NotificationListData(
            items=[NotificationPublic.model_validate(item) for item in items],
            page=page,
            size=size,
            total=total,
            total_pages=ceil(total / size) if total else 0,
        )

    async def unread_count(self, user_id: int) -> NotificationUnreadCountData:
        return NotificationUnreadCountData(unread_count=await self.repository.unread_count(user_id))

    async def get_notification(self, user_id: int, notification_id: int) -> NotificationPublic:
        notification = await self._get_notification(user_id, notification_id)
        return NotificationPublic.model_validate(notification)

    async def mark_read(self, user_id: int, notification_id: int) -> NotificationPublic:
        notification = await self._get_notification(user_id, notification_id)
        if notification.status == NotificationStatus.UNREAD:
            notification.status = NotificationStatus.READ
            notification.read_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(notification)
        return NotificationPublic.model_validate(notification)

    async def read_all(self, user_id: int) -> NotificationUnreadCountData:
        items, _total = await self.repository.list_notifications(user_id, page=1, size=1000, status=NotificationStatus.UNREAD)
        now = datetime.now(UTC)
        for item in items:
            item.status = NotificationStatus.READ
            item.read_at = now
        await self.session.commit()
        return await self.unread_count(user_id)

    async def dismiss(self, user_id: int, notification_id: int) -> NotificationPublic:
        notification = await self._get_notification(user_id, notification_id)
        if notification.status == NotificationStatus.DISMISSED:
            raise AppError("NOTIFICATION_ALREADY_DISMISSED", "이미 해제된 알림입니다.", 409)
        notification.status = NotificationStatus.DISMISSED
        notification.dismissed_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(notification)
        return NotificationPublic.model_validate(notification)

    async def archive(self, user_id: int, notification_id: int) -> NotificationPublic:
        notification = await self._get_notification(user_id, notification_id)
        notification.status = NotificationStatus.ARCHIVED
        notification.archived_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(notification)
        return NotificationPublic.model_validate(notification)

    async def list_deliveries(self, user_id: int, page: int, size: int) -> NotificationDeliveryListData:
        items, total = await self.repository.list_deliveries(user_id, page, size)
        return NotificationDeliveryListData(
            items=[NotificationDeliveryPublic.model_validate(item) for item in items],
            page=page,
            size=size,
            total=total,
            total_pages=ceil(total / size) if total else 0,
        )

    async def get_delivery(self, user_id: int, delivery_id: int) -> NotificationDeliveryPublic:
        delivery = await self._get_delivery(user_id, delivery_id)
        return NotificationDeliveryPublic.model_validate(delivery)

    async def retry_delivery(self, user_id: int, delivery_id: int) -> NotificationDeliveryPublic:
        delivery = await self._get_delivery(user_id, delivery_id)
        if delivery.status not in {NotificationDeliveryStatus.FAILED, NotificationDeliveryStatus.RETRY_SCHEDULED}:
            raise AppError("NOTIFICATION_DELIVERY_NOT_RETRYABLE", "재시도할 수 없는 delivery 상태입니다.", 409)
        if delivery.attempt_count >= 3:
            raise AppError("NOTIFICATION_DELIVERY_NOT_RETRYABLE", "최대 재시도 횟수를 초과했습니다.", 409)
        await self._send_delivery(delivery)
        await self.session.commit()
        await self.session.refresh(delivery)
        return NotificationDeliveryPublic.model_validate(delivery)

    async def create_notification(
        self,
        *,
        user_id: int,
        event_type: NotificationEventType,
        title: str,
        message: str,
        source_type: str,
        source_id: str | int,
        deduplication_key: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        source_url: str | None = None,
        scheduled_for: datetime | None = None,
        expires_at: datetime | None = None,
        payload: dict | None = None,
    ) -> Notification | None:
        setting = await self.get_or_create_setting(user_id)
        if not self._event_enabled(setting, event_type):
            return None
        existing = await self.repository.get_by_deduplication_key(deduplication_key)
        if existing:
            return existing
        if not setting.in_app_enabled and not setting.email_enabled and not setting.push_enabled:
            return None
        notification = Notification(
            user_id=user_id,
            event_type=event_type,
            priority=priority,
            title=title[:200],
            message=message,
            source_type=source_type,
            source_id=str(source_id),
            source_url=source_url,
            deduplication_key=deduplication_key,
            scheduled_for=scheduled_for,
            expires_at=expires_at,
            payload=payload,
        )
        self.session.add(notification)
        await self.session.flush()
        if setting.email_enabled:
            self.session.add(
                NotificationDelivery(
                    notification_id=notification.id,
                    user_id=user_id,
                    channel=NotificationChannel.EMAIL,
                    status=NotificationDeliveryStatus.PENDING,
                    provider=get_notification_email_provider().provider,
                )
            )
        if setting.push_enabled:
            self.session.add(
                NotificationDelivery(
                    notification_id=notification.id,
                    user_id=user_id,
                    channel=NotificationChannel.PUSH,
                    status=NotificationDeliveryStatus.SKIPPED,
                    provider="disabled",
                    error_code="NOTIFICATION_PROVIDER_DISABLED",
                    safe_error_message="Push provider는 v0.8.0에서 설정 구조만 제공합니다.",
                )
            )
        return notification

    async def run_due(self, user_id: int | None = None) -> NotificationProcessingRunPublic:
        run = NotificationProcessingRun(
            task_type=NotificationProcessingTaskType.RUN_DUE_NOTIFICATIONS,
            status=NotificationProcessingRunStatus.RUNNING,
            started_at=datetime.now(UTC),
        )
        self.session.add(run)
        await self.session.flush()
        try:
            result = {
                "schedule": await self.process_due_schedule_reminders(user_id=user_id, commit=False),
                "recommendations": await self.process_recommendation_candidates(user_id=user_id, commit=False),
                "gmail": await self.process_gmail_candidates(user_id=user_id, commit=False),
                "document_improvements": await self.process_document_improvements(user_id=user_id, commit=False),
                "sync_failures": await self.process_sync_failures(user_id=user_id, commit=False),
                "deliveries": await self.process_pending_email_deliveries(user_id=user_id, commit=False),
            }
            run.status = NotificationProcessingRunStatus.COMPLETED
            run.completed_at = datetime.now(UTC)
            run.result = result
            run.processed_count = sum(item["processed"] for item in result.values())
            run.created_count = sum(item.get("created", 0) for item in result.values())
            run.sent_count = result["deliveries"].get("sent", 0)
            run.failed_count = sum(item.get("failed", 0) for item in result.values())
            run.skipped_count = sum(item.get("skipped", 0) for item in result.values())
            await self.session.commit()
        except Exception as exc:
            run.status = NotificationProcessingRunStatus.FAILED
            run.completed_at = datetime.now(UTC)
            run.error_code = "NOTIFICATION_WORKER_FAILED"
            run.safe_error_message = str(exc)[:500]
            await self.session.commit()
            raise
        await self.session.refresh(run)
        return NotificationProcessingRunPublic.model_validate(run)

    async def process_due_schedule_reminders(self, *, user_id: int | None = None, commit: bool = True) -> dict[str, int]:
        created = skipped = failed = 0
        rows = await self.repository.due_schedule_reminders()
        for reminder, event in rows:
            if user_id is not None and reminder.user_id != user_id:
                continue
            event_type, priority = _event_type_for_schedule(event.event_type)
            notification = await self.create_notification(
                user_id=reminder.user_id,
                event_type=event_type,
                title=f"{event.title} 리마인더",
                message=f"{reminder.minutes_before}분 후 예정된 일정입니다.",
                source_type="SCHEDULE_REMINDER",
                source_id=reminder.id,
                source_url=f"/calendar/events/{event.id}",
                deduplication_key=f"schedule:{event.id}:reminder:{reminder.id}:in_app",
                priority=priority,
                scheduled_for=reminder.scheduled_at,
                expires_at=event.end_at,
            )
            if notification:
                created += 1
                reminder.status = ScheduleReminderStatus.SENT
                reminder.sent_at = datetime.now(UTC)
            else:
                skipped += 1
        if commit:
            await self.session.commit()
        return {"processed": len(rows), "created": created, "skipped": skipped, "failed": failed}

    async def process_recommendation_candidates(self, *, user_id: int | None = None, commit: bool = True) -> dict[str, int]:
        rows = await self.repository.pending_recommendation_candidates()
        created = skipped = failed = 0
        for candidate in rows:
            if user_id is not None and candidate.user_id != user_id:
                continue
            event_type = (
                NotificationEventType.JOB_RECOMMENDATION_SCORE_UP
                if candidate.notification_type == RecommendationNotificationType.RECOMMENDATION_SCORE_INCREASED
                else NotificationEventType.JOB_RECOMMENDATION_NEW
            )
            notification = await self.create_notification(
                user_id=candidate.user_id,
                event_type=event_type,
                title=candidate.title,
                message=candidate.message,
                source_type="RECOMMENDATION_NOTIFICATION_CANDIDATE",
                source_id=candidate.id,
                source_url=f"/recommendations/{candidate.recommendation_id}" if candidate.recommendation_id else "/recommendations",
                deduplication_key=f"recommendation-candidate:{candidate.id}:in_app",
                priority=NotificationPriority.NORMAL,
                payload=candidate.payload,
                expires_at=candidate.expires_at,
            )
            if notification:
                created += 1
                candidate.status = RecommendationNotificationStatus.READ
                candidate.read_at = datetime.now(UTC)
            else:
                skipped += 1
        if commit:
            await self.session.commit()
        return {"processed": len(rows), "created": created, "skipped": skipped, "failed": failed}

    async def process_gmail_candidates(self, *, user_id: int | None = None, commit: bool = True) -> dict[str, int]:
        rows = await self.repository.new_gmail_candidates()
        created = skipped = failed = 0
        for candidate in rows:
            if user_id is not None and candidate.user_id != user_id:
                continue
            notification = await self.create_notification(
                user_id=candidate.user_id,
                event_type=NotificationEventType.GMAIL_CANDIDATE_CREATED,
                title="새 채용 메일 후보가 도착했습니다.",
                message=f"{candidate.company_name or '회사 미확인'} · {candidate.job_title or candidate.candidate_type.value}",
                source_type="EMAIL_CANDIDATE",
                source_id=candidate.id,
                source_url=f"/inbox-candidates?candidateId={candidate.id}",
                deduplication_key=f"gmail-candidate:{candidate.id}:in_app",
                priority=NotificationPriority.NORMAL,
                expires_at=candidate.expires_at,
            )
            created += 1 if notification else 0
            skipped += 0 if notification else 1
        if commit:
            await self.session.commit()
        return {"processed": len(rows), "created": created, "skipped": skipped, "failed": failed}

    async def process_document_improvements(self, *, user_id: int | None = None, commit: bool = True) -> dict[str, int]:
        rows = await self.repository.completed_document_improvements()
        created = skipped = failed = 0
        for run in rows:
            if user_id is not None and run.user_id != user_id:
                continue
            is_failed = run.status == DocumentImprovementRunStatus.FAILED
            notification = await self.create_notification(
                user_id=run.user_id,
                event_type=NotificationEventType.DOCUMENT_IMPROVEMENT_FAILED if is_failed else NotificationEventType.DOCUMENT_IMPROVEMENT_COMPLETED,
                title="지원 문서 개선이 실패했습니다." if is_failed else "지원 문서 개선안이 준비되었습니다.",
                message=run.safe_error_message if is_failed and run.safe_error_message else "문장별 제안을 확인하고 승인할 수 있습니다.",
                source_type="DOCUMENT_IMPROVEMENT_RUN",
                source_id=run.id,
                source_url=f"/documents/{run.application_document_id}/improvements/{run.id}",
                deduplication_key=f"document-improvement:{run.id}:{run.status.value}:in_app",
                priority=NotificationPriority.HIGH if is_failed else NotificationPriority.NORMAL,
            )
            created += 1 if notification else 0
            skipped += 0 if notification else 1
        if commit:
            await self.session.commit()
        return {"processed": len(rows), "created": created, "skipped": skipped, "failed": failed}

    async def process_sync_failures(self, *, user_id: int | None = None, commit: bool = True) -> dict[str, int]:
        calendar_rows, gmail_rows = await self.repository.failed_sync_runs()
        created = skipped = failed = 0
        for row in calendar_rows:
            if user_id is not None and row.user_id != user_id:
                continue
            notification = await self.create_notification(
                user_id=row.user_id,
                event_type=NotificationEventType.CALENDAR_SYNC_FAILED,
                title="Google Calendar 동기화에 실패했습니다.",
                message="연동 상태를 확인해 주세요.",
                source_type="CALENDAR_SYNC_RUN",
                source_id=row.id,
                source_url="/settings/integrations",
                deduplication_key=f"calendar-sync:{row.id}:failed:in_app",
                priority=NotificationPriority.HIGH,
            )
            created += 1 if notification else 0
            skipped += 0 if notification else 1
        for row in gmail_rows:
            if user_id is not None and row.user_id != user_id:
                continue
            notification = await self.create_notification(
                user_id=row.user_id,
                event_type=NotificationEventType.GMAIL_SYNC_FAILED,
                title="Gmail 동기화에 실패했습니다.",
                message="Gmail 연동 상태를 확인해 주세요.",
                source_type="GMAIL_SYNC_RUN",
                source_id=row.id,
                source_url="/settings/integrations",
                deduplication_key=f"gmail-sync:{row.id}:failed:in_app",
                priority=NotificationPriority.HIGH,
            )
            created += 1 if notification else 0
            skipped += 0 if notification else 1
        if commit:
            await self.session.commit()
        return {"processed": len(calendar_rows) + len(gmail_rows), "created": created, "skipped": skipped, "failed": failed}

    async def process_pending_email_deliveries(self, *, user_id: int | None = None, commit: bool = True) -> dict[str, int]:
        deliveries, _total = await self.repository.list_deliveries(user_id or 0, 1, 100) if user_id else ([], 0)
        if user_id is None:
            # User-scoped APIs call this directly. Global worker email sending is intentionally conservative for v0.8.0.
            return {"processed": 0, "created": 0, "sent": 0, "failed": 0, "skipped": 0}
        sent = failed = skipped = 0
        for delivery in deliveries:
            if delivery.channel != NotificationChannel.EMAIL or delivery.status not in {NotificationDeliveryStatus.PENDING, NotificationDeliveryStatus.RETRY_SCHEDULED}:
                skipped += 1
                continue
            await self._send_delivery(delivery)
            if delivery.status == NotificationDeliveryStatus.SENT:
                sent += 1
            else:
                failed += 1
        if commit:
            await self.session.commit()
        return {"processed": len(deliveries), "created": 0, "sent": sent, "failed": failed, "skipped": skipped}

    async def _send_delivery(self, delivery: NotificationDelivery) -> None:
        user = await self.repository.get_user(delivery.user_id)
        if not user:
            delivery.status = NotificationDeliveryStatus.FAILED
            delivery.error_code = "NOTIFICATION_FORBIDDEN"
            delivery.safe_error_message = "알림 대상 사용자를 찾을 수 없습니다."
            return
        if delivery.attempt_count >= 3:
            delivery.status = NotificationDeliveryStatus.FAILED
            delivery.error_code = "NOTIFICATION_DELIVERY_NOT_RETRYABLE"
            delivery.safe_error_message = "최대 재시도 횟수를 초과했습니다."
            return
        provider = get_notification_email_provider()
        delivery.provider = provider.provider
        delivery.attempt_count += 1
        delivery.status = NotificationDeliveryStatus.PROCESSING
        try:
            result = await provider.send(to=user.email, subject=delivery.notification.title, body=delivery.notification.message)
            delivery.status = NotificationDeliveryStatus.SENT
            delivery.sent_at = datetime.now(UTC)
            delivery.provider_message_id = result.message_id
            delivery.error_code = None
            delivery.safe_error_message = None
        except AppError as exc:
            delivery.error_code = exc.code
            delivery.safe_error_message = exc.message[:500]
            if exc.code == "NOTIFICATION_PROVIDER_DISABLED":
                delivery.status = NotificationDeliveryStatus.FAILED
            elif delivery.attempt_count < 3:
                delivery.status = NotificationDeliveryStatus.RETRY_SCHEDULED
                delivery.next_retry_at = datetime.now(UTC) + _retry_delay(delivery.attempt_count)
            else:
                delivery.status = NotificationDeliveryStatus.FAILED

    async def _get_notification(self, user_id: int, notification_id: int) -> Notification:
        notification = await self.repository.get_notification(user_id, notification_id)
        if not notification:
            raise AppError("NOTIFICATION_NOT_FOUND", "알림을 찾을 수 없습니다.", 404)
        return notification

    async def _get_delivery(self, user_id: int, delivery_id: int) -> NotificationDelivery:
        delivery = await self.repository.get_delivery(user_id, delivery_id)
        if not delivery:
            raise AppError("NOTIFICATION_DELIVERY_NOT_FOUND", "알림 delivery를 찾을 수 없습니다.", 404)
        return delivery

    def _event_enabled(self, setting: NotificationSetting, event_type: NotificationEventType) -> bool:
        if event_type in {NotificationEventType.SCHEDULE_REMINDER, NotificationEventType.INTERVIEW_REMINDER, NotificationEventType.ASSESSMENT_DEADLINE}:
            return setting.schedule_reminder_enabled
        if event_type == NotificationEventType.APPLICATION_DEADLINE:
            return setting.application_deadline_enabled
        if event_type in {NotificationEventType.JOB_RECOMMENDATION_NEW, NotificationEventType.JOB_RECOMMENDATION_SCORE_UP}:
            return setting.recommendation_enabled
        if event_type == NotificationEventType.GMAIL_CANDIDATE_CREATED:
            return setting.gmail_candidate_enabled
        if event_type in {NotificationEventType.DOCUMENT_IMPROVEMENT_COMPLETED, NotificationEventType.DOCUMENT_IMPROVEMENT_FAILED}:
            return setting.document_improvement_enabled
        if event_type in {NotificationEventType.CALENDAR_SYNC_FAILED, NotificationEventType.GMAIL_SYNC_FAILED}:
            return setting.sync_error_enabled
        return True


def _event_type_for_schedule(event_type: ScheduleEventType) -> tuple[NotificationEventType, NotificationPriority]:
    if event_type in {ScheduleEventType.INTERVIEW, ScheduleEventType.FINAL_INTERVIEW}:
        return NotificationEventType.INTERVIEW_REMINDER, NotificationPriority.URGENT
    if event_type in {ScheduleEventType.ASSIGNMENT_DEADLINE, ScheduleEventType.CODING_TEST}:
        return NotificationEventType.ASSESSMENT_DEADLINE, NotificationPriority.HIGH
    if event_type == ScheduleEventType.APPLICATION_DEADLINE:
        return NotificationEventType.APPLICATION_DEADLINE, NotificationPriority.HIGH
    return NotificationEventType.SCHEDULE_REMINDER, NotificationPriority.NORMAL


def _retry_delay(attempt_count: int) -> timedelta:
    if attempt_count <= 1:
        return timedelta(minutes=1)
    if attempt_count == 2:
        return timedelta(minutes=5)
    return timedelta(minutes=30)
