import asyncio
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ["JWT_SECRET_KEY"] = "test-access-secret"
os.environ["JWT_REFRESH_SECRET_KEY"] = "test-refresh-secret"

from app.db.base import Base  # noqa: E402
from app.db.session import get_session  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    testing_session = async_sessionmaker(engine, expire_on_commit=False)

    async def init_db() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def dispose_db() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    async def override_get_session():
        async with testing_session() as session:
            yield session

    asyncio.run(init_db())
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    asyncio.run(dispose_db())


def auth_headers(client: TestClient, email: str = "profile@example.com") -> dict[str, str]:
    client.post(
        "/api/v1/auth/signup",
        json={"name": "Profile User", "email": email, "password": "password123"},
    )
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def profile_payload() -> dict:
    return {
        "display_name": "도하",
        "headline": "Backend Developer",
        "career_level": "JUNIOR",
        "years_of_experience": 2,
        "desired_job_title": "AI Backend Engineer",
        "introduction": "FastAPI와 데이터 모델링을 좋아합니다.",
    }


def test_profile_requires_authentication(client):
    response = client.get("/api/v1/profiles/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_TOKEN_MISSING"


def test_profile_create_get_update_and_duplicate_block(client):
    headers = auth_headers(client)

    created = client.post("/api/v1/profiles", json=profile_payload(), headers=headers)
    assert created.status_code == 201
    assert created.json()["data"]["career_level"] == "JUNIOR"

    duplicate = client.post("/api/v1/profiles", json=profile_payload(), headers=headers)
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "PROFILE_ALREADY_EXISTS"

    updated = client.patch(
        "/api/v1/profiles/me",
        json={"headline": "AI Service Developer", "years_of_experience": 3},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["headline"] == "AI Service Developer"

    fetched = client.get("/api/v1/profiles/me", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["data"]["years_of_experience"] == 3


def test_invalid_career_level_is_rejected(client):
    headers = auth_headers(client)
    payload = profile_payload()
    payload["career_level"] = "INVALID"

    response = client.post("/api/v1/profiles", json=payload, headers=headers)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_user_skills_crud_and_duplicate_normalization(client):
    headers = auth_headers(client)
    created = client.post(
        "/api/v1/profiles/me/skills",
        json={
            "name": " Python ",
            "category": "LANGUAGE",
            "proficiency_level": "INTERMEDIATE",
            "years_of_experience": 2,
            "is_primary": True,
        },
        headers=headers,
    )
    assert created.status_code == 201
    skill_id = created.json()["data"]["id"]

    duplicate = client.post(
        "/api/v1/profiles/me/skills",
        json={"name": "python", "proficiency_level": "BEGINNER"},
        headers=headers,
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "SKILL_ALREADY_REGISTERED"

    updated = client.patch(
        f"/api/v1/profiles/me/skills/{skill_id}",
        json={"proficiency_level": "ADVANCED", "is_primary": False},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["proficiency_level"] == "ADVANCED"

    deleted = client.delete(f"/api/v1/profiles/me/skills/{skill_id}", headers=headers)
    assert deleted.status_code == 200


def test_user_skill_ownership_is_enforced(client):
    owner_headers = auth_headers(client, "owner@example.com")
    other_headers = auth_headers(client, "other@example.com")
    created = client.post(
        "/api/v1/profiles/me/skills",
        json={"name": "FastAPI", "proficiency_level": "INTERMEDIATE"},
        headers=owner_headers,
    )
    skill_id = created.json()["data"]["id"]

    response = client.patch(
        f"/api/v1/profiles/me/skills/{skill_id}",
        json={"proficiency_level": "EXPERT"},
        headers=other_headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "USER_SKILL_NOT_FOUND"


def test_experience_crud_and_date_validation(client):
    headers = auth_headers(client)
    bad = client.post(
        "/api/v1/profiles/me/experiences",
        json={
            "company_name": "Acme",
            "position": "Developer",
            "employment_type": "FULL_TIME",
            "start_date": "2026-01-01",
            "end_date": "2025-01-01",
            "is_current": False,
        },
        headers=headers,
    )
    assert bad.status_code == 422

    created = client.post(
        "/api/v1/profiles/me/experiences",
        json={
            "company_name": "Acme",
            "position": "Developer",
            "employment_type": "FULL_TIME",
            "start_date": "2024-01-01",
            "end_date": "2025-01-01",
            "is_current": False,
            "description": "API 개발",
        },
        headers=headers,
    )
    assert created.status_code == 201
    experience_id = created.json()["data"]["id"]

    detail = client.get(f"/api/v1/profiles/me/experiences/{experience_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["data"]["company_name"] == "Acme"

    updated = client.patch(
        f"/api/v1/profiles/me/experiences/{experience_id}",
        json={"position": "Backend Developer"},
        headers=headers,
    )
    assert updated.json()["data"]["position"] == "Backend Developer"

    deleted = client.delete(f"/api/v1/profiles/me/experiences/{experience_id}", headers=headers)
    assert deleted.status_code == 200


def test_project_crud_with_skills_and_url_validation(client):
    headers = auth_headers(client)
    bad = client.post(
        "/api/v1/profiles/me/projects",
        json={
            "name": "Bad URL",
            "start_date": "2025-01-01",
            "repository_url": "javascript:alert(1)",
        },
        headers=headers,
    )
    assert bad.status_code == 422

    created = client.post(
        "/api/v1/profiles/me/projects",
        json={
            "name": "ApplyMate",
            "summary": "취업 관리 서비스",
            "role": "Backend",
            "start_date": "2025-01-01",
            "end_date": "2025-06-01",
            "repository_url": "https://github.com/DDORINY/ApplyMate-AI",
            "skill_names": ["FastAPI", "PostgreSQL"],
        },
        headers=headers,
    )
    assert created.status_code == 201
    project_id = created.json()["data"]["id"]
    assert len(created.json()["data"]["skills"]) == 2

    updated = client.patch(
        f"/api/v1/profiles/me/projects/{project_id}",
        json={"skill_names": ["FastAPI"]},
        headers=headers,
    )
    assert updated.status_code == 200
    assert len(updated.json()["data"]["skills"]) == 1

    deleted = client.delete(f"/api/v1/profiles/me/projects/{project_id}", headers=headers)
    assert deleted.status_code == 200


def test_preferences_upsert_and_validation(client):
    headers = auth_headers(client)
    bad = client.put(
        "/api/v1/profiles/me/preferences",
        json={"minimum_salary": -1},
        headers=headers,
    )
    assert bad.status_code == 422

    saved = client.put(
        "/api/v1/profiles/me/preferences",
        json={
            "preferred_employment_types": ["FULL_TIME"],
            "preferred_locations": ["Seoul", "Remote"],
            "preferred_company_sizes": ["STARTUP"],
            "remote_preference": "HYBRID",
            "minimum_salary": 40000000,
            "desired_roles": ["Backend Developer"],
            "priority_keywords": ["FastAPI"],
        },
        headers=headers,
    )
    assert saved.status_code == 200
    assert saved.json()["data"]["remote_preference"] == "HYBRID"

    fetched = client.get("/api/v1/profiles/me/preferences", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["data"]["minimum_salary"] == 40000000


def test_exclusions_crud(client):
    headers = auth_headers(client)
    created = client.post(
        "/api/v1/profiles/me/exclusions",
        json={
            "condition_type": "LOCATION",
            "value": "Far City",
            "reason": "통근 불가",
            "is_active": True,
        },
        headers=headers,
    )
    assert created.status_code == 201
    condition_id = created.json()["data"]["id"]

    updated = client.patch(
        f"/api/v1/profiles/me/exclusions/{condition_id}",
        json={"is_active": False},
        headers=headers,
    )
    assert updated.json()["data"]["is_active"] is False

    deleted = client.delete(f"/api/v1/profiles/me/exclusions/{condition_id}", headers=headers)
    assert deleted.status_code == 200


def test_portfolio_links_crud_url_validation_and_primary_handling(client):
    headers = auth_headers(client)
    bad = client.post(
        "/api/v1/profiles/me/portfolio-links",
        json={"link_type": "GITHUB", "title": "Bad", "url": "file:///secret"},
        headers=headers,
    )
    assert bad.status_code == 422

    first = client.post(
        "/api/v1/profiles/me/portfolio-links",
        json={
            "link_type": "GITHUB",
            "title": "GitHub",
            "url": "https://github.com/DDORINY",
            "is_primary": True,
        },
        headers=headers,
    )
    second = client.post(
        "/api/v1/profiles/me/portfolio-links",
        json={
            "link_type": "BLOG",
            "title": "Blog",
            "url": "https://example.com",
            "is_primary": True,
        },
        headers=headers,
    )
    assert first.status_code == 201
    assert second.status_code == 201

    links = client.get("/api/v1/profiles/me/portfolio-links", headers=headers).json()["data"]
    assert sum(1 for link in links if link["is_primary"]) == 1

    deleted = client.delete(
        f"/api/v1/profiles/me/portfolio-links/{second.json()['data']['id']}", headers=headers
    )
    assert deleted.status_code == 200
