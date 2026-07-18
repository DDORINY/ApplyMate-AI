from __future__ import annotations

# ruff: noqa: F811

import asyncio
from io import BytesIO

from sqlalchemy import select

from app.models.job import Company, JobPosting
from app.services import job_url_importer
from test_auth import client, login, signup  # noqa: F401


def auth_headers(client) -> dict[str, str]:
    signup(client, email="jobs@example.com")
    response = login(client, email="jobs@example.com")
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def job_payload(**overrides):
    payload = {
        "company_name": "Example  Company",
        "company_website_url": "https://example.com",
        "company_size": "STARTUP",
        "title": "AI Backend Developer",
        "position": "Backend Developer",
        "employment_type": "FULL_TIME",
        "career_requirement": "신입 가능",
        "education_requirement": "무관",
        "location": "서울",
        "work_type": "HYBRID",
        "salary_min": 3000,
        "salary_max": 5000,
        "salary_text": "회사 내규",
        "description": "주요 업무",
        "requirements": "Python",
        "preferred_qualifications": "FastAPI",
        "benefits": "점심 제공",
        "recruitment_process": "서류 > 면접",
        "deadline_at": "2026-08-31T14:59:59Z",
        "deadline_type": "FIXED",
        "status": "SAVED",
        "is_favorite": False,
        "source_type": "MANUAL",
        "source_url": None,
        "notes": "확인 필요",
    }
    payload.update(overrides)
    return payload


async def companies(testing_session) -> list[Company]:
    async with testing_session() as session:
        result = await session.execute(select(Company))
        return list(result.scalars())


async def jobs(testing_session) -> list[JobPosting]:
    async with testing_session() as session:
        result = await session.execute(select(JobPosting))
        return list(result.scalars())


def test_create_job_requires_auth(client):
    response = client.post("/api/v1/jobs", json=job_payload())

    assert response.status_code == 401


def test_create_job_creates_company_and_job(client):
    headers = auth_headers(client)

    response = client.post("/api/v1/jobs", json=job_payload(), headers=headers)

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["title"] == "AI Backend Developer"
    assert data["company"]["normalized_name"] == "example company"
    assert data["company"]["company_size"] == "STARTUP"
    assert len(asyncio.run(companies(client.testing_session))) == 1
    assert len(asyncio.run(jobs(client.testing_session))) == 1


def test_company_is_reused_by_normalized_name(client):
    headers = auth_headers(client)
    assert (
        client.post("/api/v1/jobs", json=job_payload(title="A"), headers=headers).status_code == 201
    )

    response = client.post(
        "/api/v1/jobs",
        json=job_payload(company_name=" example company ", title="B"),
        headers=headers,
    )

    assert response.status_code == 201
    assert len(asyncio.run(companies(client.testing_session))) == 1


def test_duplicate_job_blocked_for_same_user(client):
    headers = auth_headers(client)
    assert client.post("/api/v1/jobs", json=job_payload(), headers=headers).status_code == 201

    response = client.post("/api/v1/jobs", json=job_payload(), headers=headers)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "JOB_POSTING_ALREADY_EXISTS"


def test_same_job_allowed_for_other_user(client):
    first_headers = auth_headers(client)
    assert client.post("/api/v1/jobs", json=job_payload(), headers=first_headers).status_code == 201
    client.cookies.clear()
    signup(client, email="other@example.com")
    other_access = login(client, email="other@example.com").json()["data"]["access_token"]

    response = client.post(
        "/api/v1/jobs",
        json=job_payload(),
        headers={"Authorization": f"Bearer {other_access}"},
    )

    assert response.status_code == 201


def test_create_job_rejects_invalid_salary_range(client):
    headers = auth_headers(client)

    response = client.post(
        "/api/v1/jobs",
        json=job_payload(salary_min=6000, salary_max=5000),
        headers=headers,
    )

    assert response.status_code == 422


def test_list_jobs_supports_search_filter_sort_and_pagination(client):
    headers = auth_headers(client)
    client.post(
        "/api/v1/jobs", json=job_payload(title="Backend", status="INTERESTED"), headers=headers
    )
    client.post(
        "/api/v1/jobs",
        json=job_payload(
            title="Frontend", employment_type="CONTRACT", deadline_at="2026-09-01T00:00:00Z"
        ),
        headers=headers,
    )

    response = client.get(
        "/api/v1/jobs?query=back&status=INTERESTED&sort=title&order=asc&page=1&size=10",
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Backend"


def test_detail_update_delete_and_ownership(client):
    headers = auth_headers(client)
    created = client.post("/api/v1/jobs", json=job_payload(), headers=headers).json()["data"]
    job_id = created["id"]

    detail = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    update = client.patch(
        f"/api/v1/jobs/{job_id}",
        json={"status": "REVIEWING", "is_favorite": True, "notes": "지원 검토"},
        headers=headers,
    )
    delete_response = client.delete(f"/api/v1/jobs/{job_id}", headers=headers)
    missing = client.get(f"/api/v1/jobs/{job_id}", headers=headers)

    assert detail.status_code == 200
    assert update.status_code == 200
    assert update.json()["data"]["status"] == "REVIEWING"
    assert update.json()["data"]["is_favorite"] is True
    assert delete_response.status_code == 200
    assert missing.status_code == 404


class FakeResponse(BytesIO):
    status = 200

    def __init__(self, body: bytes, content_type: str = "text/html") -> None:
        super().__init__(body)
        self.headers = {"Content-Type": content_type}


def test_import_url_blocks_localhost(client):
    headers = auth_headers(client)

    response = client.post(
        "/api/v1/jobs/import-url", json={"url": "http://localhost/job"}, headers=headers
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "JOB_POSTING_URL_BLOCKED"


def test_import_url_uses_user_input_over_extracted_fields(client, monkeypatch):
    headers = auth_headers(client)

    class FakeOpener:
        def open(self, _request, timeout):  # noqa: ANN001
            return FakeResponse(
                b"<html><head><title>Extracted Title</title><meta name='description' content='Meta desc'></head><body>Body text</body></html>"
            )

    monkeypatch.setattr(
        job_url_importer.socket,
        "getaddrinfo",
        lambda *_args: [(None, None, None, None, ("93.184.216.34", 0))],
    )
    monkeypatch.setattr(job_url_importer, "build_opener", lambda *_args: FakeOpener())

    response = client.post(
        "/api/v1/jobs/import-url",
        json={
            "url": "https://example.com/jobs/1",
            "company_name": "Manual Company",
            "title": "Manual Title",
            "description": "Manual Description",
        },
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["job"]["title"] == "Manual Title"
    assert data["job"]["description"] == "Manual Description"
    assert data["job"]["source_type"] == "URL"
    assert "title" in data["extracted_fields"]


def test_import_url_rejects_duplicate_url(client, monkeypatch):
    headers = auth_headers(client)

    class FakeOpener:
        def open(self, _request, timeout):  # noqa: ANN001
            return FakeResponse(b"<html><head><title>Job</title></head><body>Body</body></html>")

    monkeypatch.setattr(
        job_url_importer.socket,
        "getaddrinfo",
        lambda *_args: [(None, None, None, None, ("93.184.216.34", 0))],
    )
    monkeypatch.setattr(job_url_importer, "build_opener", lambda *_args: FakeOpener())

    payload = {"url": "https://example.com/jobs/2", "company_name": "Example", "title": "Job"}
    assert client.post("/api/v1/jobs/import-url", json=payload, headers=headers).status_code == 201
    response = client.post("/api/v1/jobs/import-url", json=payload, headers=headers)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "JOB_POSTING_ALREADY_EXISTS"
