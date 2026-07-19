import os
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

# ruff: noqa: F811

os.environ["JWT_SECRET_KEY"] = "test-access-secret"
os.environ["JWT_REFRESH_SECRET_KEY"] = "test-refresh-secret"
os.environ["EMAIL_PROVIDER"] = "development"
os.environ["AI_PROVIDER"] = "mock"
os.environ["AI_ANALYSIS_COOLDOWN_SECONDS"] = "0"
os.environ["AI_DAILY_ANALYSIS_LIMIT"] = "20"

from test_auth import client, login, signup  # noqa: E402,F401


def auth_headers(client: TestClient, email: str = "dashboard@example.com") -> dict[str, str]:
    signup(client, email=email)
    response = login(client, email=email)
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def create_job(client: TestClient, headers: dict[str, str], *, suffix: str, deadline_at: str | None = None) -> int:
    response = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "company_name": f"Dashboard Co {suffix}",
            "company_website_url": f"https://example.com/{suffix}",
            "company_size": "STARTUP",
            "title": f"Backend Engineer {suffix}",
            "position": "Backend Engineer",
            "employment_type": "FULL_TIME",
            "career_requirement": "Junior",
            "education_requirement": "None",
            "location": "Seoul",
            "work_type": "HYBRID",
            "description": "Build APIs.",
            "requirements": "Python, FastAPI",
            "preferred_qualifications": "PostgreSQL",
            "deadline_at": deadline_at,
            "deadline_type": "FIXED" if deadline_at else "UNKNOWN",
            "status": "SAVED",
            "source_type": "MANUAL",
            "source_url": f"https://example.com/jobs/{suffix}",
        },
    )
    assert response.status_code == 201
    return int(response.json()["data"]["id"])


def create_resume(client: TestClient, headers: dict[str, str]) -> int:
    response = client.post(
        "/api/v1/resumes",
        headers=headers,
        json={"title": "Dashboard Resume", "description": "Primary resume"},
    )
    assert response.status_code == 201
    return int(response.json()["data"]["id"])


def create_application(
    client: TestClient,
    headers: dict[str, str],
    *,
    suffix: str,
    status: str = "PREPARING",
    planned_apply_at: str | None = None,
) -> dict:
    job_id = create_job(client, headers, suffix=suffix)
    resume_id = create_resume(client, headers)
    response = client.post(
        "/api/v1/applications",
        headers=headers,
        json={
            "job_id": job_id,
            "resume_id": resume_id,
            "status": status,
            "planned_apply_at": planned_apply_at,
            "application_channel": "COMPANY_SITE",
            "application_url": f"https://example.com/apply/{suffix}",
            "priority": "HIGH",
        },
    )
    assert response.status_code == 201
    return response.json()["data"]


def create_event(
    client: TestClient,
    headers: dict[str, str],
    *,
    title: str,
    start_at: datetime,
    end_at: datetime,
    event_type: str = "INTERVIEW",
    status: str = "SCHEDULED",
    application_id: int | None = None,
    job_id: int | None = None,
) -> dict:
    response = client.post(
        "/api/v1/calendar/events",
        headers=headers,
        json={
            "application_id": application_id,
            "job_id": job_id,
            "title": title,
            "event_type": event_type,
            "status": status,
            "confidence": "USER_INPUT",
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
            "timezone": "Asia/Seoul",
        },
    )
    assert response.status_code == 201
    return response.json()["data"]


def create_profile_inputs(client: TestClient, headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/profiles",
        headers=headers,
        json={
            "display_name": "Dashboard User",
            "headline": "Backend Developer",
            "career_level": "JUNIOR",
            "years_of_experience": 2,
            "desired_job_title": "Backend Engineer",
            "introduction": "Python backend developer.",
        },
    )
    assert response.status_code == 201
    response = client.post(
        "/api/v1/profiles/me/skills",
        headers=headers,
        json={
            "name": "Python",
            "category": "BACKEND",
            "proficiency_level": "INTERMEDIATE",
            "years_of_experience": 2,
            "is_primary": True,
        },
    )
    assert response.status_code == 201
    response = client.put(
        "/api/v1/profiles/me/preferences",
        headers=headers,
        json={
            "preferred_employment_types": ["FULL_TIME"],
            "preferred_locations": ["Seoul"],
            "preferred_company_sizes": ["STARTUP"],
            "remote_preference": "HYBRID",
            "minimum_salary": 3000,
            "desired_roles": ["Backend Engineer"],
            "priority_keywords": ["FastAPI"],
        },
    )
    assert response.status_code == 200
    response = client.post(
        "/api/v1/profiles/me/projects",
        headers=headers,
        json={
            "name": "Dashboard Project",
            "summary": "Job management dashboard.",
            "role": "Backend Developer",
            "start_date": "2025-01-01",
            "skill_names": ["Python"],
        },
    )
    assert response.status_code == 201


def test_dashboard_empty_state_requires_auth(client: TestClient):
    unauthorized = client.get("/api/v1/dashboard")
    headers = auth_headers(client, "dashboard-empty@example.com")

    response = client.get("/api/v1/dashboard", headers=headers)

    assert unauthorized.status_code == 401
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["summary"]["total_applications"] == 0
    assert data["application_activity"]["new_applications"] == 0
    assert all(item["count"] == 0 for item in data["application_status_counts"])
    assert data["today_events"] == []
    assert data["recent_activities"] == []


def test_dashboard_groups_statuses_and_excludes_archived_applications(client: TestClient):
    headers = auth_headers(client, "dashboard-status@example.com")
    saved = create_application(client, headers, suffix="saved", status="SAVED")
    create_application(client, headers, suffix="preparing", status="PREPARING")
    create_application(client, headers, suffix="review", status="DOCUMENT_REVIEW")
    create_application(client, headers, suffix="coding", status="CODING_TEST")
    create_application(client, headers, suffix="interview", status="FINAL_INTERVIEW")
    create_application(client, headers, suffix="offer", status="OFFER")
    create_application(client, headers, suffix="rejected", status="REJECTED")
    assert client.delete(f"/api/v1/applications/{saved['id']}", headers=headers).status_code == 200

    response = client.get("/api/v1/dashboard?period=all", headers=headers)

    assert response.status_code == 200
    counts = {item["group"]: item for item in response.json()["data"]["application_status_counts"]}
    assert counts["PREPARING"]["count"] == 1
    assert counts["IN_PROGRESS"]["count"] == 2
    assert counts["INTERVIEW"]["count"] == 1
    assert counts["OFFER"]["count"] == 1
    assert counts["REJECTED"]["count"] == 1
    assert counts["PREPARING"]["statuses"] == ["SAVED", "PREPARING"]
    assert response.json()["data"]["summary"]["total_applications"] == 6


def test_dashboard_returns_today_week_deadlines_and_due_soon_jobs(client: TestClient):
    headers = auth_headers(client, "dashboard-schedule@example.com")
    tz = ZoneInfo("Asia/Seoul")
    now_local = datetime.now(tz)
    today_start = now_local.replace(hour=10, minute=0, second=0, microsecond=0)
    if today_start <= now_local:
        today_start = now_local + timedelta(hours=1)
    application = create_application(client, headers, suffix="schedule")
    create_event(
        client,
        headers,
        application_id=application["id"],
        title="Interview today",
        start_at=today_start,
        end_at=today_start + timedelta(hours=1),
    )
    create_event(
        client,
        headers,
        application_id=application["id"],
        title="Application deadline",
        start_at=now_local + timedelta(days=2),
        end_at=now_local + timedelta(days=2, hours=1),
        event_type="APPLICATION_DEADLINE",
    )
    cancelled = create_event(
        client,
        headers,
        title="Cancelled deadline",
        start_at=now_local + timedelta(days=3),
        end_at=now_local + timedelta(days=3, hours=1),
        event_type="APPLICATION_DEADLINE",
    )
    assert (
        client.post(f"/api/v1/calendar/events/{cancelled['id']}/status", headers=headers, json={"status": "CANCELLED"})
        .status_code
        == 200
    )
    deadline = (datetime.now(UTC) + timedelta(days=3)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    create_job(client, headers, suffix="due-soon", deadline_at=deadline)

    response = client.get("/api/v1/dashboard?timezone=Asia/Seoul&recent_limit=10", headers=headers)

    assert response.status_code == 200
    data = response.json()["data"]
    assert any(item["title"] == "Interview today" for item in data["today_events"])
    assert any(item["title"] == "Application deadline" for item in data["week_events"])
    assert [item["title"] for item in data["upcoming_deadlines"]] == ["Application deadline"]
    assert any(item["kind"] == "JOB" and item["job_title"] == "Backend Engineer due-soon" for item in data["due_soon_jobs"])


def test_dashboard_period_filters_custom_dates_and_invalid_timezone(client: TestClient):
    headers = auth_headers(client, "dashboard-period@example.com")
    create_application(client, headers, suffix="period")

    custom = client.get(
        "/api/v1/dashboard?start_date=2026-01-01&end_date=2026-12-31&timezone=Asia/Seoul",
        headers=headers,
    )
    invalid_range = client.get("/api/v1/dashboard?start_date=2026-12-31&end_date=2026-01-01", headers=headers)
    invalid_timezone = client.get("/api/v1/dashboard?timezone=Invalid/Timezone", headers=headers)

    assert custom.status_code == 200
    assert custom.json()["data"]["period_start"].startswith("2025-12-31T15:00:00")
    assert invalid_range.status_code == 400
    assert invalid_range.json()["error"]["code"] == "DASHBOARD_INVALID_DATE_RANGE"
    assert invalid_timezone.status_code == 400
    assert invalid_timezone.json()["error"]["code"] == "DASHBOARD_INVALID_TIMEZONE"


def test_dashboard_limits_recent_ai_sections_and_isolates_users(client: TestClient):
    first_headers = auth_headers(client, "dashboard-ai-owner@example.com")
    create_profile_inputs(client, first_headers)
    job_id = create_job(client, first_headers, suffix="ai-owner")
    assert client.post(f"/api/v1/jobs/{job_id}/analysis", json={"force": False}, headers=first_headers).status_code == 200
    assert client.post(f"/api/v1/jobs/{job_id}/match", json={"force": False}, headers=first_headers).status_code == 200
    client.cookies.clear()
    second_headers = auth_headers(client, "dashboard-ai-other@example.com")

    owner = client.get("/api/v1/dashboard?recent_limit=1", headers=first_headers)
    other = client.get("/api/v1/dashboard?recent_limit=1", headers=second_headers)

    assert owner.status_code == 200
    assert len(owner.json()["data"]["recent_job_analyses"]) == 1
    assert len(owner.json()["data"]["recent_matches"]) == 1
    assert owner.json()["data"]["recent_activities"]
    assert other.status_code == 200
    assert other.json()["data"]["recent_job_analyses"] == []
    assert other.json()["data"]["recent_matches"] == []
