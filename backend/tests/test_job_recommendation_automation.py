from __future__ import annotations

# ruff: noqa: F811

from test_auth import client, login, signup  # noqa: F401
from test_job_match import create_job_and_analysis, create_profile_inputs


def auth_headers(client, email: str = "recommend-auto@example.com") -> dict[str, str]:
    signup(client, email=email)
    response = login(client, email=email)
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def test_recommendation_settings_default_and_update(client):
    headers = auth_headers(client)

    default_response = client.get("/api/v1/recommendations/settings", headers=headers)
    update_response = client.patch(
        "/api/v1/recommendations/settings",
        json={"enabled": True, "frequency": "DAILY", "minimum_score": 70, "preferred_run_hour": 8},
        headers=headers,
    )

    assert default_response.status_code == 200
    assert default_response.json()["data"]["enabled"] is False
    assert default_response.json()["data"]["frequency"] == "MANUAL"
    assert update_response.status_code == 200
    assert update_response.json()["data"]["enabled"] is True
    assert update_response.json()["data"]["frequency"] == "DAILY"
    assert update_response.json()["data"]["minimum_score"] == 70
    assert update_response.json()["data"]["next_run_at"] is not None


def test_run_if_due_creates_snapshot_and_notifications(client):
    headers = auth_headers(client, email="recommend-auto-run@example.com")
    create_profile_inputs(client, headers)
    create_job_and_analysis(client, headers)

    run_response = client.post("/api/v1/recommendations/jobs/run-if-due", json={"force": True}, headers=headers)
    snapshots_response = client.get("/api/v1/recommendations/jobs/snapshots", headers=headers)
    recommendations_response = client.get("/api/v1/recommendations/jobs", headers=headers)
    notifications_response = client.get("/api/v1/recommendation-notifications", headers=headers)

    assert run_response.status_code == 200
    assert run_response.json()["data"]["executed"] is True
    assert run_response.json()["data"]["snapshot_id"] is not None
    assert snapshots_response.status_code == 200
    snapshot = snapshots_response.json()["data"]["items"][0]
    assert snapshot["new_count"] == 1
    assert snapshot["items"][0]["change_type"] == "NEW"
    assert recommendations_response.json()["data"]["items"][0]["latest_change_type"] == "NEW"
    assert notifications_response.status_code == 200


def test_run_if_due_returns_skip_reason(client):
    headers = auth_headers(client, email="recommend-auto-skip@example.com")
    create_profile_inputs(client, headers)
    create_job_and_analysis(client, headers)

    response = client.post("/api/v1/recommendations/jobs/run-if-due", json={}, headers=headers)

    assert response.status_code == 200
    assert response.json()["data"]["executed"] is False
    assert response.json()["data"]["skip_reason"] == "DISABLED"


def test_snapshot_ownership_blocks_other_user(client):
    headers = auth_headers(client, email="recommend-auto-owner@example.com")
    create_profile_inputs(client, headers)
    create_job_and_analysis(client, headers)
    run_response = client.post("/api/v1/recommendations/jobs/run-if-due", json={"force": True}, headers=headers)
    snapshot_id = run_response.json()["data"]["snapshot_id"]
    other_headers = auth_headers(client, email="recommend-auto-other@example.com")

    response = client.get(f"/api/v1/recommendations/jobs/snapshots/{snapshot_id}", headers=other_headers)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RECOMMENDATION_SNAPSHOT_NOT_FOUND"
