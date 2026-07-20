import os

# ruff: noqa: F811

os.environ["JWT_SECRET_KEY"] = "test-access-secret"
os.environ["JWT_REFRESH_SECRET_KEY"] = "test-refresh-secret"
os.environ["EMAIL_PROVIDER"] = "development"
os.environ["AI_PROVIDER"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402

from test_applications import (  # noqa: E402
    auth_headers,
    create_application_payload,
    create_job,
    create_resume,
)
from test_auth import client  # noqa: E402,F401


def create_application(client: TestClient, headers: dict[str, str], job_id: int | None = None) -> dict:
    if job_id is None:
        job_id = create_job(client, headers)
    resume_id = create_resume(client, headers)
    response = client.post(
        "/api/v1/applications",
        headers=headers,
        json=create_application_payload(job_id, resume_id),
    )
    assert response.status_code == 201
    return response.json()["data"]


def event_payload(**overrides) -> dict:
    payload = {
        "title": "1차 면접",
        "event_type": "INTERVIEW",
        "status": "SCHEDULED",
        "confidence": "USER_INPUT",
        "start_at": "2026-07-25T10:00:00+09:00",
        "end_at": "2026-07-25T11:00:00+09:00",
        "timezone": "Asia/Seoul",
        "location": "Seoul",
        "reminders": [{"reminder_type": "IN_APP", "minutes_before": 60}],
    }
    payload.update(overrides)
    return payload


def create_event(client: TestClient, headers: dict[str, str], **overrides) -> dict:
    response = client.post("/api/v1/calendar/events", headers=headers, json=event_payload(**overrides))
    assert response.status_code == 201
    return response.json()["data"]


def test_schedule_event_crud_list_archive_and_history(client: TestClient):
    headers = auth_headers(client, "schedule-crud@example.com")
    application = create_application(client, headers)

    created = create_event(client, headers, application_id=application["id"], title="서류 마감")
    detail = client.get(f"/api/v1/calendar/events/{created['id']}", headers=headers)
    listed = client.get("/api/v1/calendar/events?event_type=INTERVIEW", headers=headers)
    updated = client.patch(
        f"/api/v1/calendar/events/{created['id']}",
        headers=headers,
        json={"title": "서류 마감 준비", "confidence": "CONFIRMED"},
    )
    history = client.get(f"/api/v1/calendar/events/{created['id']}/history", headers=headers)
    archived = client.delete(f"/api/v1/calendar/events/{created['id']}", headers=headers)
    default_list = client.get("/api/v1/calendar/events", headers=headers)
    archived_list = client.get("/api/v1/calendar/events?include_archived=true", headers=headers)

    assert detail.status_code == 200
    assert detail.json()["data"]["application_id"] == application["id"]
    assert listed.json()["data"]["total"] == 1
    assert updated.json()["data"]["title"] == "서류 마감 준비"
    assert [item["action"] for item in history.json()["data"]][-1] == "CREATED"
    assert archived.json()["data"]["archived"] is True
    assert default_list.json()["data"]["total"] == 0
    assert archived_list.json()["data"]["total"] == 1


def test_schedule_rejects_invalid_time_range_and_timezone(client: TestClient):
    headers = auth_headers(client, "schedule-time@example.com")

    invalid_range = client.post(
        "/api/v1/calendar/events",
        headers=headers,
        json=event_payload(start_at="2026-07-25T11:00:00+09:00", end_at="2026-07-25T10:00:00+09:00"),
    )
    naive_datetime = client.post(
        "/api/v1/calendar/events",
        headers=headers,
        json=event_payload(start_at="2026-07-25T10:00:00", end_at="2026-07-25T11:00:00"),
    )
    invalid_timezone = client.post(
        "/api/v1/calendar/events",
        headers=headers,
        json=event_payload(timezone="Invalid/Timezone"),
    )

    assert invalid_range.status_code == 422
    assert naive_datetime.status_code == 422
    assert invalid_timezone.status_code == 422


def test_schedule_linking_blocks_application_job_mismatch(client: TestClient):
    headers = auth_headers(client, "schedule-link@example.com")
    first_job_id = create_job(client, headers, "FirstCo")
    second_job_id = create_job(client, headers, "SecondCo")
    application = create_application(client, headers, first_job_id)

    response = client.post(
        "/api/v1/calendar/events",
        headers=headers,
        json=event_payload(application_id=application["id"], job_id=second_job_id),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "SCHEDULE_EVENT_RELATION_INVALID"


def test_schedule_status_complete_cancel_and_reminder_inactivation(client: TestClient):
    headers = auth_headers(client, "schedule-status@example.com")
    event = create_event(client, headers)

    completed = client.post(
        f"/api/v1/calendar/events/{event['id']}/status",
        headers=headers,
        json={"status": "COMPLETED"},
    )
    duplicate_completed = client.post(
        f"/api/v1/calendar/events/{event['id']}/status",
        headers=headers,
        json={"status": "COMPLETED"},
    )
    reminders = client.get(f"/api/v1/calendar/events/{event['id']}/reminders", headers=headers)

    assert completed.status_code == 200
    assert completed.json()["data"]["completed_at"] is not None
    assert duplicate_completed.status_code == 400
    assert duplicate_completed.json()["error"]["code"] == "SCHEDULE_EVENT_ALREADY_COMPLETED"
    assert reminders.json()["data"][0]["status"] == "INACTIVE"


def test_schedule_reminder_create_update_duplicate_and_delete(client: TestClient):
    headers = auth_headers(client, "schedule-reminder@example.com")
    event = create_event(client, headers, reminders=[])

    created = client.post(
        f"/api/v1/calendar/events/{event['id']}/reminders",
        headers=headers,
        json={"reminder_type": "IN_APP", "minutes_before": 30},
    )
    duplicate = client.post(
        f"/api/v1/calendar/events/{event['id']}/reminders",
        headers=headers,
        json={"reminder_type": "IN_APP", "minutes_before": 30},
    )
    updated = client.patch(
        f"/api/v1/calendar/events/{event['id']}/reminders/{created.json()['data']['id']}",
        headers=headers,
        json={"minutes_before": 10},
    )
    deleted = client.delete(
        f"/api/v1/calendar/events/{event['id']}/reminders/{created.json()['data']['id']}",
        headers=headers,
    )

    assert created.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "SCHEDULE_REMINDER_DUPLICATE"
    assert updated.json()["data"]["minutes_before"] == 10
    assert deleted.json()["data"]["deleted"] is True


def test_schedule_conflicts_and_boundary_non_overlap(client: TestClient):
    headers = auth_headers(client, "schedule-conflict@example.com")
    first = create_event(
        client,
        headers,
        title="코딩 테스트",
        start_at="2026-07-25T10:00:00+09:00",
        end_at="2026-07-25T11:00:00+09:00",
    )
    second = create_event(
        client,
        headers,
        title="과제",
        start_at="2026-07-25T10:30:00+09:00",
        end_at="2026-07-25T11:30:00+09:00",
    )

    assert first["has_conflict"] is False
    assert second["has_conflict"] is True

    overlap = client.get(
        "/api/v1/calendar/conflicts?start_at=2026-07-25T10:30:00%2B09:00&end_at=2026-07-25T11:30:00%2B09:00",
        headers=headers,
    )
    boundary = client.get(
        "/api/v1/calendar/conflicts?start_at=2026-07-25T11:30:00%2B09:00&end_at=2026-07-25T12:00:00%2B09:00",
        headers=headers,
    )

    assert {item["title"] for item in overlap.json()["data"]} == {"코딩 테스트", "과제"}
    assert boundary.json()["data"] == []


def test_schedule_upcoming_overdue_and_ownership(client: TestClient):
    first_headers = auth_headers(client, "schedule-owner@example.com")
    overdue = create_event(
        client,
        first_headers,
        title="지난 마감",
        start_at="2026-01-01T10:00:00+09:00",
        end_at="2026-01-01T11:00:00+09:00",
    )
    upcoming = create_event(
        client,
        first_headers,
        title="다가오는 일정",
        start_at="2026-07-21T10:00:00+09:00",
        end_at="2026-07-21T11:00:00+09:00",
    )
    second_headers = auth_headers(client, "schedule-other@example.com")

    overdue_detail = client.get(f"/api/v1/calendar/events/{overdue['id']}", headers=first_headers)
    upcoming_list = client.get("/api/v1/calendar/upcoming?hours=168", headers=first_headers)
    forbidden = client.get(f"/api/v1/calendar/events/{upcoming['id']}", headers=second_headers)

    assert overdue_detail.json()["data"]["effective_status"] == "MISSED"
    assert overdue_detail.json()["data"]["is_overdue"] is True
    assert upcoming_list.status_code == 200
    assert any(item["title"] == "다가오는 일정" for item in upcoming_list.json()["data"]["items"])
    assert forbidden.status_code == 404
