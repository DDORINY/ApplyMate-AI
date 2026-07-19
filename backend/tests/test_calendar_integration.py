import os
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

# ruff: noqa: F811

os.environ["JWT_SECRET_KEY"] = "test-access-secret"
os.environ["JWT_REFRESH_SECRET_KEY"] = "test-refresh-secret"
os.environ["EMAIL_PROVIDER"] = "development"
os.environ["AI_PROVIDER"] = "mock"
os.environ["CALENDAR_PROVIDER"] = "mock"
os.environ["EXTERNAL_TOKEN_ENCRYPTION_KEY"] = "test-calendar-token-encryption-key"
os.environ["EXTERNAL_TOKEN_ENCRYPTION_KEY_VERSION"] = "test-v1"

from app.core.config import get_settings  # noqa: E402
from test_auth import client, login, signup  # noqa: E402,F401


def auth_headers(client: TestClient, email: str = "calendar-integration@example.com") -> dict[str, str]:
    signup(client, email=email)
    token = login(client, email=email).json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_event(client: TestClient, headers: dict[str, str], title: str = "Google sync interview") -> dict:
    start = datetime.now().astimezone() + timedelta(days=1)
    end = start + timedelta(hours=1)
    response = client.post(
        "/api/v1/calendar/events",
        headers=headers,
        json={
            "title": title,
            "event_type": "INTERVIEW",
            "status": "SCHEDULED",
            "confidence": "USER_INPUT",
            "start_at": start.isoformat(),
            "end_at": end.isoformat(),
            "timezone": "Asia/Seoul",
            "location": "Seoul",
        },
    )
    assert response.status_code == 201
    return response.json()["data"]


def connect_mock_calendar(client: TestClient, headers: dict[str, str]) -> dict:
    get_settings.cache_clear()
    response = client.post(
        "/api/v1/integrations/calendar/connect",
        headers=headers,
        json={"redirect_path": "/settings/integrations"},
    )
    assert response.status_code == 200
    authorization_url = response.json()["data"]["authorization_url"]
    params = parse_qs(urlparse(authorization_url).query)
    callback = client.get(
        f"/api/v1/integrations/calendar/callback?state={params['state'][0]}&code={params['code'][0]}"
    )
    assert callback.status_code == 200
    return callback.json()["data"]


def test_calendar_connection_flow_lists_and_selects_calendars(client: TestClient):
    headers = auth_headers(client)

    initial = client.get("/api/v1/integrations/calendar/status", headers=headers)
    connected = connect_mock_calendar(client, headers)
    status = client.get("/api/v1/integrations/calendar/status", headers=headers)
    calendars = client.get("/api/v1/integrations/calendar/calendars", headers=headers)
    readonly = client.patch(
        "/api/v1/integrations/calendar/settings",
        headers=headers,
        json={"selected_calendar_id": "mock-readonly"},
    )
    selected = client.patch(
        "/api/v1/integrations/calendar/settings",
        headers=headers,
        json={"selected_calendar_id": "mock-primary", "sync_direction": "INTERNAL_TO_GOOGLE"},
    )

    assert initial.status_code == 200
    assert initial.json()["data"]["connected"] is False
    assert connected["connected"] is True
    assert status.json()["data"]["connected"] is True
    assert "access-token" not in str(status.json()).lower()
    assert "refresh-token" not in str(status.json()).lower()
    assert len(calendars.json()["data"]) == 2
    assert readonly.status_code == 400
    assert readonly.json()["error"]["code"] == "CALENDAR_NOT_WRITABLE"
    assert selected.status_code == 200
    assert selected.json()["data"]["selected_calendar_id"] == "mock-primary"


def test_calendar_sync_creates_mapping_and_updates_existing_mapping(client: TestClient):
    headers = auth_headers(client, "calendar-sync@example.com")
    connect_mock_calendar(client, headers)
    event = create_event(client, headers)

    first = client.post(f"/api/v1/calendar/events/{event['id']}/sync", headers=headers)
    second = client.post(f"/api/v1/calendar/events/{event['id']}/sync", headers=headers)
    status = client.get(f"/api/v1/calendar/events/{event['id']}/sync-status", headers=headers)
    runs = client.get("/api/v1/integrations/calendar/sync-runs", headers=headers)

    assert first.status_code == 200
    assert first.json()["data"]["run"]["created_count"] == 1
    assert first.json()["data"]["mappings"][0]["external_event_id"] == f"mock-event-{event['id']}"
    assert second.status_code == 200
    assert second.json()["data"]["run"]["updated_count"] == 1
    assert status.json()["data"]["mapping"]["sync_status"] == "SYNCED"
    assert len(runs.json()["data"]) == 2


def test_calendar_sync_all_disconnect_and_ownership(client: TestClient):
    owner_headers = auth_headers(client, "calendar-owner@example.com")
    connect_mock_calendar(client, owner_headers)
    owner_event = create_event(client, owner_headers, "Owner event")
    create_event(client, owner_headers, "Owner second event")
    other_headers = auth_headers(client, "calendar-other@example.com")

    forbidden = client.post(f"/api/v1/calendar/events/{owner_event['id']}/sync", headers=other_headers)
    sync_all = client.post("/api/v1/integrations/calendar/sync", headers=owner_headers)
    disconnected = client.delete("/api/v1/integrations/calendar/connection", headers=owner_headers)
    after_disconnect = client.post("/api/v1/integrations/calendar/sync", headers=owner_headers)

    assert forbidden.status_code == 404
    assert sync_all.status_code == 200
    assert sync_all.json()["data"]["run"]["created_count"] == 2
    assert disconnected.status_code == 200
    assert disconnected.json()["data"]["disconnected"] is True
    assert after_disconnect.status_code == 404


def test_calendar_oauth_rejects_reused_and_invalid_state(client: TestClient):
    headers = auth_headers(client, "calendar-state@example.com")
    response = client.post("/api/v1/integrations/calendar/connect", headers=headers, json={})
    params = parse_qs(urlparse(response.json()["data"]["authorization_url"]).query)
    state = params["state"][0]
    code = params["code"][0]

    first = client.get(f"/api/v1/integrations/calendar/callback?state={state}&code={code}")
    reused = client.get(f"/api/v1/integrations/calendar/callback?state={state}&code={code}")
    invalid = client.get("/api/v1/integrations/calendar/callback?state=invalid&code=mock")

    assert first.status_code == 200
    assert reused.status_code == 400
    assert reused.json()["error"]["code"] == "CALENDAR_OAUTH_STATE_INVALID"
    assert invalid.status_code == 400
    assert invalid.json()["error"]["code"] == "CALENDAR_OAUTH_STATE_INVALID"
