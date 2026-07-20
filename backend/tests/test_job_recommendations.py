from __future__ import annotations

# ruff: noqa: F811

from test_auth import client, login, signup  # noqa: F401
from test_job_match import create_job_and_analysis, create_profile_inputs


def auth_headers(client, email: str = "recommend@example.com") -> dict[str, str]:
    signup(client, email=email)
    response = login(client, email=email)
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def test_job_recommendation_requires_auth(client):
    response = client.post("/api/v1/recommendations/jobs/generate", json={})

    assert response.status_code == 401


def test_generate_rule_based_recommendations_and_list_detail(client):
    headers = auth_headers(client)
    create_profile_inputs(client, headers)
    create_job_and_analysis(client, headers)

    generated = client.post(
        "/api/v1/recommendations/jobs/generate",
        json={"force_refresh": False, "include_jobs_without_analysis": True, "exclude_applied_jobs": True},
        headers=headers,
    )
    listed = client.get("/api/v1/recommendations/jobs", headers=headers)

    assert generated.status_code == 200
    assert generated.json()["data"]["recommended_count"] == 1
    assert listed.status_code == 200
    item = listed.json()["data"]["items"][0]
    assert item["recommendation_type"] == "RULE_BASED"
    assert 0 <= item["score"] <= 100
    assert item["grade"] in {"EXCELLENT", "GOOD", "POSSIBLE", "LOW", "BLOCKED"}
    assert item["reasons"]

    detail = client.get(f"/api/v1/recommendations/jobs/{item['id']}", headers=headers)

    assert detail.status_code == 200
    assert detail.json()["data"]["id"] == item["id"]
    assert detail.json()["data"]["score_breakdown"]["skill"] >= 0


def test_feedback_hides_and_excludes_next_generation(client):
    headers = auth_headers(client, email="recommend-feedback@example.com")
    create_profile_inputs(client, headers)
    create_job_and_analysis(client, headers)
    assert client.post("/api/v1/recommendations/jobs/generate", json={}, headers=headers).status_code == 200
    item = client.get("/api/v1/recommendations/jobs", headers=headers).json()["data"]["items"][0]

    feedback = client.post(
        f"/api/v1/recommendations/jobs/{item['id']}/feedback",
        json={"feedback_type": "HIDDEN", "reason_code": "ROLE", "comment": "Not for me."},
        headers=headers,
    )
    hidden_list = client.get("/api/v1/recommendations/jobs", headers=headers)
    visible_with_hidden = client.get("/api/v1/recommendations/jobs?include_hidden=true", headers=headers)
    second_run = client.post("/api/v1/recommendations/jobs/generate", json={}, headers=headers)

    assert feedback.status_code == 201
    assert hidden_list.json()["data"]["total"] == 0
    assert visible_with_hidden.json()["data"]["items"][0]["feedback"]["feedback_type"] == "HIDDEN"
    assert second_run.json()["data"]["excluded_count"] >= 1


def test_recommendation_ownership_blocks_other_user(client):
    headers = auth_headers(client, email="recommend-owner@example.com")
    create_profile_inputs(client, headers)
    create_job_and_analysis(client, headers)
    assert client.post("/api/v1/recommendations/jobs/generate", json={}, headers=headers).status_code == 200
    recommendation_id = client.get("/api/v1/recommendations/jobs", headers=headers).json()["data"]["items"][0]["id"]
    other_headers = auth_headers(client, email="recommend-other@example.com")

    response = client.get(f"/api/v1/recommendations/jobs/{recommendation_id}", headers=other_headers)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "JOB_RECOMMENDATION_NOT_FOUND"


def test_policy_endpoint_declares_rule_based(client):
    headers = auth_headers(client, email="recommend-policy@example.com")

    response = client.get("/api/v1/recommendations/jobs/policy", headers=headers)

    assert response.status_code == 200
    assert response.json()["data"]["recommendation_type"] == "RULE_BASED"
    assert "AI" not in response.json()["data"]["note"].split("추천")[0]
