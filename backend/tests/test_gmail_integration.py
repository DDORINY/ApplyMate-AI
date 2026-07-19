import os
import asyncio
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

# ruff: noqa: F811

os.environ["JWT_SECRET_KEY"] = "test-access-secret"
os.environ["JWT_REFRESH_SECRET_KEY"] = "test-refresh-secret"
os.environ["EMAIL_PROVIDER"] = "development"
os.environ["AI_PROVIDER"] = "mock"
os.environ["GMAIL_PROVIDER"] = "mock"
os.environ["EXTERNAL_TOKEN_ENCRYPTION_KEY"] = "test-gmail-token-encryption-key"
os.environ["EXTERNAL_TOKEN_ENCRYPTION_KEY_VERSION"] = "test-v1"

from app.core.config import get_settings  # noqa: E402
from app.models.application import Application  # noqa: E402
from sqlalchemy import select  # noqa: E402
from test_auth import client, login, signup  # noqa: E402,F401


def auth_headers(client: TestClient, email: str = "gmail-integration@example.com") -> dict[str, str]:
    signup(client, email=email)
    token = login(client, email=email).json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def connect_mock_gmail(client: TestClient, headers: dict[str, str]) -> dict:
    get_settings.cache_clear()
    response = client.post("/api/v1/integrations/gmail/connect", headers=headers, json={"redirect_path": "/settings/integrations"})
    assert response.status_code == 200
    params = parse_qs(urlparse(response.json()["data"]["authorization_url"]).query)
    callback = client.get(f"/api/v1/integrations/gmail/callback?state={params['state'][0]}&code={params['code'][0]}")
    assert callback.status_code == 200
    return callback.json()["data"]


def create_application(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/applications",
        headers=headers,
        json={
            "status": "APPLIED",
            "application_channel": "EMAIL",
            "priority": "NORMAL",
        },
    )
    assert response.status_code == 201, response.json()
    data = response.json()["data"]

    async def set_snapshot() -> None:
        async with client.testing_session() as session:
            application = (await session.execute(select(Application).where(Application.id == data["id"]))).scalar_one()
            application.company_name_snapshot = "Bravo"
            application.job_title_snapshot = "프론트엔드 개발자"
            await session.commit()

    asyncio.run(set_snapshot())
    return client.get(f"/api/v1/applications/{data['id']}", headers=headers).json()["data"]


def test_gmail_connection_sync_and_duplicate_skip(client: TestClient):
    headers = auth_headers(client)
    initial = client.get("/api/v1/integrations/gmail/status", headers=headers)
    connected = connect_mock_gmail(client, headers)
    first = client.post("/api/v1/integrations/gmail/sync", headers=headers)
    second = client.post("/api/v1/integrations/gmail/sync", headers=headers)
    candidates = client.get("/api/v1/email-candidates", headers=headers)
    runs = client.get("/api/v1/integrations/gmail/sync-runs", headers=headers)

    assert initial.status_code == 200
    assert initial.json()["data"]["connected"] is False
    assert connected["connected"] is True
    assert first.status_code == 200
    assert first.json()["data"]["run"]["candidate_count"] == 4
    assert second.status_code == 200
    assert second.json()["data"]["run"]["ignored_count"] == 4
    assert candidates.json()["data"]["total"] == 4
    assert len(runs.json()["data"]) == 2
    assert "mock-gmail-access-credential" not in str(candidates.json())


def test_gmail_candidate_link_approve_status_and_schedule(client: TestClient):
    headers = auth_headers(client, "gmail-approve@example.com")
    connect_mock_gmail(client, headers)
    application = create_application(client, headers)
    client.post("/api/v1/integrations/gmail/sync", headers=headers)
    candidates = client.get("/api/v1/email-candidates?candidate_type=INTERVIEW", headers=headers)
    candidate_id = candidates.json()["data"]["items"][0]["id"]

    options = client.get(f"/api/v1/email-candidates/{candidate_id}/application-options", headers=headers)
    linked = client.post(f"/api/v1/email-candidates/{candidate_id}/link-application?application_id={application['id']}", headers=headers)
    approved = client.post(
        f"/api/v1/email-candidates/{candidate_id}/approve",
        headers=headers,
        json={"apply_status_change": True, "create_schedule_event": True},
    )
    duplicate = client.post(f"/api/v1/email-candidates/{candidate_id}/approve", headers=headers, json={"apply_status_change": True})
    refreshed = client.get(f"/api/v1/applications/{application['id']}", headers=headers)
    schedules = client.get("/api/v1/calendar/events?application_id=" + str(application["id"]), headers=headers)

    assert options.status_code == 200
    assert options.json()["data"]["items"][0]["match_type"] in {"EXACT", "LIKELY"}
    assert linked.status_code == 200
    assert approved.status_code == 200
    assert approved.json()["data"]["candidate"]["status"] == "APPLIED"
    assert duplicate.status_code == 409
    assert refreshed.json()["data"]["status"] == "INTERVIEW"
    assert schedules.json()["data"]["total"] == 1


def test_gmail_candidate_reject_and_ownership(client: TestClient):
    owner_headers = auth_headers(client, "gmail-owner@example.com")
    connect_mock_gmail(client, owner_headers)
    client.post("/api/v1/integrations/gmail/sync", headers=owner_headers)
    candidate_id = client.get("/api/v1/email-candidates", headers=owner_headers).json()["data"]["items"][0]["id"]
    other_headers = auth_headers(client, "gmail-other@example.com")

    forbidden = client.get(f"/api/v1/email-candidates/{candidate_id}", headers=other_headers)
    rejected = client.post(f"/api/v1/email-candidates/{candidate_id}/reject", headers=owner_headers, json={"reason": "not useful"})

    assert forbidden.status_code == 404
    assert rejected.status_code == 200
    assert rejected.json()["data"]["status"] == "REJECTED"


def test_gmail_oauth_rejects_reused_and_invalid_state(client: TestClient):
    headers = auth_headers(client, "gmail-state@example.com")
    response = client.post("/api/v1/integrations/gmail/connect", headers=headers, json={})
    params = parse_qs(urlparse(response.json()["data"]["authorization_url"]).query)
    state = params["state"][0]
    code = params["code"][0]

    first = client.get(f"/api/v1/integrations/gmail/callback?state={state}&code={code}")
    reused = client.get(f"/api/v1/integrations/gmail/callback?state={state}&code={code}")
    invalid = client.get("/api/v1/integrations/gmail/callback?state=invalid&code=mock")

    assert first.status_code == 200
    assert reused.status_code == 400
    assert reused.json()["error"]["code"] == "GMAIL_OAUTH_STATE_INVALID"
    assert invalid.status_code == 400
    assert invalid.json()["error"]["code"] == "GMAIL_OAUTH_STATE_INVALID"
