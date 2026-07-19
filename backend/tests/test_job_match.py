from __future__ import annotations

# ruff: noqa: F811

import asyncio

from sqlalchemy import select

from app.models.job import JobMatchRun
from test_auth import client, login, signup  # noqa: F401
from test_job_analysis import set_ai_env
from test_jobs import job_payload


def auth_headers(client, email: str = "match@example.com") -> dict[str, str]:
    signup(client, email=email)
    response = login(client, email=email)
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def create_profile_inputs(client, headers, *, add_exclusion: bool = False) -> None:
    response = client.post(
        "/api/v1/profiles",
        json={
            "display_name": "Doha",
            "headline": "AI Backend Developer",
            "career_level": "JUNIOR",
            "years_of_experience": 2,
            "desired_job_title": "Backend Developer",
            "introduction": "Python and FastAPI backend developer.",
        },
        headers=headers,
    )
    assert response.status_code == 201
    for skill in ["Python", "FastAPI"]:
        response = client.post(
            "/api/v1/profiles/me/skills",
            json={
                "name": skill,
                "category": "BACKEND",
                "proficiency_level": "INTERMEDIATE",
                "years_of_experience": 2,
                "is_primary": True,
            },
            headers=headers,
        )
        assert response.status_code == 201
    response = client.put(
        "/api/v1/profiles/me/preferences",
        json={
            "preferred_employment_types": ["FULL_TIME"],
            "preferred_locations": ["Seoul"],
            "preferred_company_sizes": ["STARTUP"],
            "remote_preference": "HYBRID",
            "minimum_salary": 3000,
            "desired_roles": ["Backend Developer"],
            "priority_keywords": ["FastAPI"],
        },
        headers=headers,
    )
    assert response.status_code == 200
    response = client.post(
        "/api/v1/profiles/me/projects",
        json={
            "name": "ApplyMate",
            "summary": "AI job manager",
            "role": "Backend Developer",
            "start_date": "2025-01-01",
            "skill_names": ["Python", "FastAPI"],
        },
        headers=headers,
    )
    assert response.status_code == 201
    if add_exclusion:
        response = client.post(
            "/api/v1/profiles/me/exclusions",
            json={
                "condition_type": "LOCATION",
                "value": "Seoul",
                "reason": "Avoid this location for test",
                "is_active": True,
            },
            headers=headers,
        )
        assert response.status_code == 201


def create_job_and_analysis(client, headers, **job_overrides) -> int:
    set_ai_env("mock")
    response = client.post(
        "/api/v1/jobs",
        json=job_payload(
            requirements="Python, FastAPI",
            preferred_qualifications="PostgreSQL",
            description="Build backend APIs with Python and FastAPI.",
            **job_overrides,
        ),
        headers=headers,
    )
    assert response.status_code == 201
    job_id = response.json()["data"]["id"]
    response = client.post(f"/api/v1/jobs/{job_id}/analysis", json={"force": False}, headers=headers)
    assert response.status_code == 200
    return job_id


async def match_runs(testing_session) -> list[JobMatchRun]:
    async with testing_session() as session:
        result = await session.execute(select(JobMatchRun))
        return list(result.scalars())


def test_job_match_requires_auth(client):
    response = client.post("/api/v1/jobs/1/match", json={"force": False})

    assert response.status_code == 401


def test_job_match_requires_completed_job_analysis(client):
    headers = auth_headers(client)
    create_profile_inputs(client, headers)
    response = client.post("/api/v1/jobs", json=job_payload(), headers=headers)
    assert response.status_code == 201
    job_id = response.json()["data"]["id"]

    response = client.post(f"/api/v1/jobs/{job_id}/match", json={"force": False}, headers=headers)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "JOB_ANALYSIS_REQUIRED"


def test_job_match_calculates_scores_and_reuses_current_result(client):
    headers = auth_headers(client)
    create_profile_inputs(client, headers)
    job_id = create_job_and_analysis(client, headers)

    first = client.post(f"/api/v1/jobs/{job_id}/match", json={"force": False}, headers=headers)
    second = client.post(f"/api/v1/jobs/{job_id}/match", json={"force": False}, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    data = first.json()["data"]
    assert data["status"] == "COMPLETED"
    assert 0 <= data["total_score"] <= 100
    assert data["is_outdated"] is False
    assert any(item["name"] == "Python" for item in data["matched_skills"])
    assert len(asyncio.run(match_runs(client.testing_session))) == 1


def test_force_job_match_creates_additional_run(client):
    headers = auth_headers(client)
    create_profile_inputs(client, headers)
    job_id = create_job_and_analysis(client, headers)
    assert client.post(f"/api/v1/jobs/{job_id}/match", json={"force": False}, headers=headers).status_code == 200

    response = client.post(f"/api/v1/jobs/{job_id}/match", json={"force": True}, headers=headers)

    assert response.status_code == 200
    assert len(asyncio.run(match_runs(client.testing_session))) == 2


def test_job_match_blocks_outdated_job_analysis(client):
    headers = auth_headers(client)
    create_profile_inputs(client, headers)
    job_id = create_job_and_analysis(client, headers)
    client.patch(
        f"/api/v1/jobs/{job_id}",
        json={"requirements": "Python, FastAPI, PostgreSQL, Redis"},
        headers=headers,
    )

    response = client.post(f"/api/v1/jobs/{job_id}/match", json={"force": False}, headers=headers)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "JOB_ANALYSIS_OUTDATED"


def test_existing_job_match_becomes_outdated_when_profile_changes(client):
    headers = auth_headers(client)
    create_profile_inputs(client, headers)
    job_id = create_job_and_analysis(client, headers)
    assert client.post(f"/api/v1/jobs/{job_id}/match", json={"force": False}, headers=headers).status_code == 200
    client.post(
        "/api/v1/profiles/me/skills",
        json={"name": "Redis", "proficiency_level": "BEGINNER"},
        headers=headers,
    )

    response = client.get(f"/api/v1/jobs/{job_id}/match", headers=headers)

    assert response.status_code == 200
    assert response.json()["data"]["is_outdated"] is True


def test_job_match_feedback_crud(client):
    headers = auth_headers(client)
    create_profile_inputs(client, headers)
    job_id = create_job_and_analysis(client, headers)
    assert client.post(f"/api/v1/jobs/{job_id}/match", json={"force": False}, headers=headers).status_code == 200

    created = client.post(
        f"/api/v1/jobs/{job_id}/match/feedback",
        json={"feedback_type": "ACCURATE", "rating": 5, "comment": "Looks right."},
        headers=headers,
    )
    feedback_id = created.json()["data"]["id"]
    listed = client.get(f"/api/v1/jobs/{job_id}/match/feedback", headers=headers)
    updated = client.patch(
        f"/api/v1/jobs/{job_id}/match/feedback/{feedback_id}",
        json={"feedback_type": "TOO_HIGH", "rating": 3},
        headers=headers,
    )
    deleted = client.delete(f"/api/v1/jobs/{job_id}/match/feedback/{feedback_id}", headers=headers)

    assert created.status_code == 201
    assert listed.status_code == 200
    assert len(listed.json()["data"]["items"]) == 1
    assert updated.status_code == 200
    assert updated.json()["data"]["feedback_type"] == "TOO_HIGH"
    assert deleted.status_code == 200


def test_exclusion_condition_makes_match_not_recommended(client):
    headers = auth_headers(client)
    create_profile_inputs(client, headers, add_exclusion=True)
    job_id = create_job_and_analysis(client, headers, location="Seoul")

    response = client.post(f"/api/v1/jobs/{job_id}/match", json={"force": False}, headers=headers)

    assert response.status_code == 200
    assert response.json()["data"]["recommendation_status"] == "NOT_RECOMMENDED"
    assert response.json()["data"]["risks"]
