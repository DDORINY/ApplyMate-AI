import asyncio
import os
from datetime import UTC, datetime, timedelta

# ruff: noqa: F811

os.environ["JWT_SECRET_KEY"] = "test-access-secret"
os.environ["JWT_REFRESH_SECRET_KEY"] = "test-refresh-secret"
os.environ["EMAIL_PROVIDER"] = "development"
os.environ["AI_PROVIDER"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.models.audit import AuditLog  # noqa: E402
from app.models.notification import Notification, NotificationDelivery  # noqa: E402
from app.models.schedule import ScheduleReminder, ScheduleReminderStatus  # noqa: E402
from app.notifications.providers.mock import clear_mock_notification_email_outbox, mock_notification_email_outbox  # noqa: E402
from test_auth import client  # noqa: E402,F401
from test_schedule import auth_headers, create_event  # noqa: E402


async def make_reminder_due(testing_session, event_id: int) -> int:
    async with testing_session() as session:
        reminder = await session.scalar(select(ScheduleReminder).where(ScheduleReminder.event_id == event_id))
        assert reminder is not None
        reminder.scheduled_at = datetime.now(UTC) - timedelta(minutes=1)
        await session.commit()
        return int(reminder.id)


async def notification_count(testing_session) -> int:
    async with testing_session() as session:
        result = await session.execute(select(Notification))
        return len(result.scalars().all())


async def delivery_statuses(testing_session) -> list[str]:
    async with testing_session() as session:
        result = await session.execute(select(NotificationDelivery))
        return [item.status.value for item in result.scalars().all()]


async def audit_actions(testing_session) -> list[str]:
    async with testing_session() as session:
        result = await session.execute(select(AuditLog).order_by(AuditLog.id))
        return [item.action for item in result.scalars().all()]


async def reminder_status(testing_session, reminder_id: int) -> str:
    async with testing_session() as session:
        reminder = await session.get(ScheduleReminder, reminder_id)
        assert reminder is not None
        return reminder.status.value


def test_notification_settings_defaults_and_update(client: TestClient):
    headers = auth_headers(client, "notification-settings@example.com")

    defaults = client.get("/api/v1/notification-settings", headers=headers)
    assert defaults.status_code == 200
    assert defaults.json()["data"]["in_app_enabled"] is True
    assert defaults.json()["data"]["email_enabled"] is False

    updated = client.patch(
        "/api/v1/notification-settings",
        headers=headers,
        json={"email_enabled": True, "timezone": "Asia/Seoul", "default_reminder_minutes": 45},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["email_enabled"] is True
    assert updated.json()["data"]["default_reminder_minutes"] == 45
    assert "NOTIFICATION_SETTINGS_UPDATED" in asyncio.run(audit_actions(client.testing_session))

    invalid = client.patch("/api/v1/notification-settings", headers=headers, json={"timezone": "Invalid/Timezone"})
    assert invalid.status_code == 400
    assert invalid.json()["error"]["code"] == "NOTIFICATION_SETTINGS_INVALID"


def test_due_schedule_reminder_creates_in_app_notification_idempotently(client: TestClient):
    headers = auth_headers(client, "notification-due@example.com")
    event = create_event(client, headers)
    reminder_id = asyncio.run(make_reminder_due(client.testing_session, event["id"]))

    first = client.post("/api/v1/notifications/run-due", headers=headers)
    second = client.post("/api/v1/notifications/run-due", headers=headers)
    unread = client.get("/api/v1/notifications/unread-count", headers=headers)
    listed = client.get("/api/v1/notifications", headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert asyncio.run(notification_count(client.testing_session)) == 1
    assert asyncio.run(reminder_status(client.testing_session, reminder_id)) == ScheduleReminderStatus.SENT.value
    assert unread.json()["data"]["unread_count"] == 1
    assert listed.json()["data"]["items"][0]["event_type"] == "INTERVIEW_REMINDER"


def test_notification_read_dismiss_archive_and_ownership(client: TestClient):
    headers = auth_headers(client, "notification-actions@example.com")
    event = create_event(client, headers)
    asyncio.run(make_reminder_due(client.testing_session, event["id"]))
    assert client.post("/api/v1/notifications/run-due", headers=headers).status_code == 200
    notification_id = client.get("/api/v1/notifications", headers=headers).json()["data"]["items"][0]["id"]

    read = client.patch(f"/api/v1/notifications/{notification_id}/read", headers=headers)
    dismissed = client.patch(f"/api/v1/notifications/{notification_id}/dismiss", headers=headers)
    archived = client.patch(f"/api/v1/notifications/{notification_id}/archive", headers=headers)
    other_headers = auth_headers(client, "notification-other@example.com")
    blocked = client.get(f"/api/v1/notifications/{notification_id}", headers=other_headers)

    assert read.json()["data"]["status"] == "READ"
    assert dismissed.json()["data"]["status"] == "DISMISSED"
    assert archived.json()["data"]["status"] == "ARCHIVED"
    assert blocked.status_code == 404
    assert blocked.json()["error"]["code"] == "NOTIFICATION_NOT_FOUND"


def test_email_delivery_uses_mock_provider_when_enabled(client: TestClient):
    clear_mock_notification_email_outbox()
    headers = auth_headers(client, "notification-email@example.com")
    assert client.patch("/api/v1/notification-settings", headers=headers, json={"email_enabled": True}).status_code == 200
    event = create_event(client, headers)
    asyncio.run(make_reminder_due(client.testing_session, event["id"]))

    response = client.post("/api/v1/notifications/run-due", headers=headers)
    deliveries = client.get("/api/v1/notification-deliveries", headers=headers)

    assert response.status_code == 200
    assert deliveries.status_code == 200
    assert asyncio.run(delivery_statuses(client.testing_session)) == ["SENT"]
    assert mock_notification_email_outbox
    assert mock_notification_email_outbox[0]["to"] == "notification-email@example.com"
