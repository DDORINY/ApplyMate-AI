import os

# ruff: noqa: F811

os.environ["JWT_SECRET_KEY"] = "test-access-secret"
os.environ["JWT_REFRESH_SECRET_KEY"] = "test-refresh-secret"
os.environ["EMAIL_PROVIDER"] = "development"
os.environ["AI_PROVIDER"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402

from test_auth import client, login, signup  # noqa: E402,F401


def auth_headers(client: TestClient, email: str = "applicant@example.com") -> dict[str, str]:
    signup(client, email=email)
    token = login(client, email=email).json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_job(client: TestClient, headers: dict[str, str], company: str = "ApplyMate") -> int:
    response = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "company_name": company,
            "title": "Backend Engineer",
            "position": "Backend Engineer",
            "description": "FastAPI service development",
            "requirements": "Python, FastAPI, PostgreSQL",
            "source_url": f"https://example.com/jobs/{company.lower()}",
        },
    )
    assert response.status_code == 201
    return int(response.json()["data"]["id"])


def create_resume(client: TestClient, headers: dict[str, str], title: str = "Main Resume") -> int:
    response = client.post(
        "/api/v1/resumes",
        headers=headers,
        json={"title": title, "description": "Primary application resume"},
    )
    assert response.status_code == 201
    return int(response.json()["data"]["id"])


def upload_resume_file(client: TestClient, headers: dict[str, str], resume_id: int) -> int:
    response = client.post(
        f"/api/v1/resumes/{resume_id}/files",
        headers={"Authorization": headers["Authorization"]},
        files={"file": ("resume.pdf", b"%PDF-1.4\n% test resume", "application/pdf")},
    )
    assert response.status_code == 201
    return int(response.json()["data"]["id"])


def create_document(client: TestClient, headers: dict[str, str], job_id: int, resume_id: int) -> int:
    response = client.post(
        "/api/v1/documents",
        headers=headers,
        json={
            "title": "Backend Engineer Cover Letter",
            "document_type": "MOTIVATION",
            "job_id": job_id,
            "resume_id": resume_id,
            "question": "Why do you want to apply?",
            "instructions": "Use only verified experience.",
            "tone": "PROFESSIONAL",
        },
    )
    assert response.status_code == 201
    return int(response.json()["data"]["id"])


def create_document_version(client: TestClient, headers: dict[str, str], document_id: int, content: str) -> int:
    response = client.post(
        f"/api/v1/documents/{document_id}/versions",
        headers=headers,
        json={"content": content, "change_summary": "submission version"},
    )
    assert response.status_code == 201
    return int(response.json()["data"]["id"])


def create_application_payload(
    job_id: int,
    resume_id: int,
    resume_file_id: int | None = None,
    document_id: int | None = None,
    version_id: int | None = None,
) -> dict[str, object]:
    return {
        "job_id": job_id,
        "resume_id": resume_id,
        "resume_file_id": resume_file_id,
        "application_document_id": document_id,
        "application_document_version_id": version_id,
        "status": "PREPARING",
        "planned_apply_at": "2026-07-25T09:00:00+09:00",
        "application_channel": "COMPANY_SITE",
        "application_url": "https://example.com/apply",
        "priority": "HIGH",
        "contact_name": "Recruiter",
        "contact_email": "recruiter@example.com",
    }


def test_application_crud_and_initial_status_history(client: TestClient):
    headers = auth_headers(client)
    job_id = create_job(client, headers)
    resume_id = create_resume(client, headers)
    file_id = upload_resume_file(client, headers, resume_id)
    document_id = create_document(client, headers, job_id, resume_id)
    version_id = create_document_version(client, headers, document_id, "Verified submission draft")

    response = client.post(
        "/api/v1/applications",
        headers=headers,
        json=create_application_payload(job_id, resume_id, file_id, document_id, version_id),
    )

    assert response.status_code == 201
    application = response.json()["data"]
    assert application["status"] == "PREPARING"
    assert application["company_name_snapshot"] == "ApplyMate"
    assert application["application_document_version_id"] == version_id

    detail = client.get(f"/api/v1/applications/{application['id']}", headers=headers)
    history = client.get(f"/api/v1/applications/{application['id']}/status-history", headers=headers)

    assert detail.status_code == 200
    assert history.status_code == 200
    assert history.json()["data"][0]["new_status"] == "PREPARING"


def test_status_change_allows_skip_and_records_history(client: TestClient):
    headers = auth_headers(client)
    job_id = create_job(client, headers)
    resume_id = create_resume(client, headers)
    created = client.post(
        "/api/v1/applications",
        headers=headers,
        json=create_application_payload(job_id, resume_id),
    ).json()["data"]

    response = client.post(
        f"/api/v1/applications/{created['id']}/status",
        headers=headers,
        json={"status": "OFFER", "reason": "fast track", "note": "Skipped intermediate stages"},
    )
    history = client.get(f"/api/v1/applications/{created['id']}/status-history", headers=headers)

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "OFFER"
    assert [item["new_status"] for item in history.json()["data"]] == ["OFFER", "PREPARING"]


def test_notes_create_update_pin_and_delete(client: TestClient):
    headers = auth_headers(client)
    job_id = create_job(client, headers)
    resume_id = create_resume(client, headers)
    application = client.post(
        "/api/v1/applications",
        headers=headers,
        json=create_application_payload(job_id, resume_id),
    ).json()["data"]

    created = client.post(
        f"/api/v1/applications/{application['id']}/notes",
        headers=headers,
        json={"content": "Interview prep memo", "note_type": "INTERVIEW"},
    )
    note_id = created.json()["data"]["id"]
    updated = client.patch(
        f"/api/v1/applications/{application['id']}/notes/{note_id}",
        headers=headers,
        json={"content": "Pinned memo", "is_pinned": True},
    )
    listed = client.get(f"/api/v1/applications/{application['id']}/notes", headers=headers)
    deleted = client.delete(f"/api/v1/applications/{application['id']}/notes/{note_id}", headers=headers)

    assert created.status_code == 201
    assert updated.json()["data"]["is_pinned"] is True
    assert listed.json()["data"][0]["content"] == "Pinned memo"
    assert deleted.json()["data"]["deleted"] is True


def test_application_list_filters_sort_and_archive(client: TestClient):
    headers = auth_headers(client)
    first_job = create_job(client, headers, "ApplyMate")
    second_job = create_job(client, headers, "CodexWorks")
    resume_id = create_resume(client, headers)
    first = client.post(
        "/api/v1/applications",
        headers=headers,
        json=create_application_payload(first_job, resume_id),
    ).json()["data"]
    client.post(
        "/api/v1/applications",
        headers=headers,
        json={**create_application_payload(second_job, resume_id), "priority": "LOW", "status": "APPLIED"},
    )

    filtered = client.get("/api/v1/applications?status=APPLIED&company=Codex", headers=headers)
    sorted_response = client.get("/api/v1/applications?sort=priority&order=asc", headers=headers)
    archived = client.delete(f"/api/v1/applications/{first['id']}", headers=headers)
    archived_list = client.get("/api/v1/applications?archived=true", headers=headers)

    assert filtered.json()["data"]["total"] == 1
    assert sorted_response.status_code == 200
    assert archived.json()["data"]["archived"] is True
    assert archived_list.json()["data"]["total"] == 1


def test_application_blocks_cross_user_access(client: TestClient):
    first_headers = auth_headers(client, "first-app@example.com")
    job_id = create_job(client, first_headers)
    resume_id = create_resume(client, first_headers)
    application = client.post(
        "/api/v1/applications",
        headers=first_headers,
        json=create_application_payload(job_id, resume_id),
    ).json()["data"]
    second_headers = auth_headers(client, "second-app@example.com")

    response = client.get(f"/api/v1/applications/{application['id']}", headers=second_headers)
    update = client.post(
        f"/api/v1/applications/{application['id']}/status",
        headers=second_headers,
        json={"status": "APPLIED"},
    )

    assert response.status_code == 404
    assert update.status_code == 404


def test_application_rejects_invalid_resume_file_relation(client: TestClient):
    headers = auth_headers(client)
    job_id = create_job(client, headers)
    first_resume = create_resume(client, headers, "First")
    second_resume = create_resume(client, headers, "Second")
    second_file = upload_resume_file(client, headers, second_resume)

    response = client.post(
        "/api/v1/applications",
        headers=headers,
        json=create_application_payload(job_id, first_resume, resume_file_id=second_file),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "APPLICATION_INVALID_RELATION"


def test_application_document_version_is_fixed_after_new_versions(client: TestClient):
    headers = auth_headers(client)
    job_id = create_job(client, headers)
    resume_id = create_resume(client, headers)
    document_id = create_document(client, headers, job_id, resume_id)
    submitted_version = create_document_version(client, headers, document_id, "Submitted version")
    application = client.post(
        "/api/v1/applications",
        headers=headers,
        json=create_application_payload(job_id, resume_id, document_id=document_id, version_id=submitted_version),
    ).json()["data"]

    create_document_version(client, headers, document_id, "Later edit")
    detail = client.get(f"/api/v1/applications/{application['id']}", headers=headers)

    assert detail.json()["data"]["application_document_version_id"] == submitted_version


def test_application_options_are_user_owned(client: TestClient):
    first_headers = auth_headers(client, "options-first@example.com")
    job_id = create_job(client, first_headers)
    resume_id = create_resume(client, first_headers)
    document_id = create_document(client, first_headers, job_id, resume_id)
    create_document_version(client, first_headers, document_id, "Version")
    second_headers = auth_headers(client, "options-second@example.com")
    create_job(client, second_headers, "OtherCo")

    first_options = client.get("/api/v1/applications/options", headers=first_headers)
    second_options = client.get("/api/v1/applications/options", headers=second_headers)

    assert first_options.status_code == 200
    assert len(first_options.json()["data"]["jobs"]) == 1
    assert len(first_options.json()["data"]["application_documents"]) == 1
    assert second_options.status_code == 200
    assert len(second_options.json()["data"]["jobs"]) == 1
    assert second_options.json()["data"]["jobs"][0]["label"].startswith("OtherCo")
