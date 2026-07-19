import os

# ruff: noqa: F811

os.environ["JWT_SECRET_KEY"] = "test-access-secret"
os.environ["JWT_REFRESH_SECRET_KEY"] = "test-refresh-secret"
os.environ["EMAIL_PROVIDER"] = "development"
os.environ["AI_PROVIDER"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402

from test_auth import client, login, signup  # noqa: E402,F401


def auth_headers(client: TestClient, email: str = "user@example.com") -> dict[str, str]:
    signup(client, email=email)
    token = login(client, email=email).json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_job(client: TestClient, headers: dict[str, str]) -> int:
    response = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "company_name": "ApplyMate",
            "title": "Backend Engineer",
            "position": "Backend Engineer",
            "description": "FastAPI 기반 채용 관리 서비스를 개발합니다.",
            "requirements": "Python, FastAPI, PostgreSQL 경험",
            "preferred_qualifications": "Docker 운영 경험",
        },
    )
    assert response.status_code == 201
    return int(response.json()["data"]["id"])


def create_document(client: TestClient, headers: dict[str, str], job_id: int | None = None) -> int:
    response = client.post(
        "/api/v1/documents",
        headers=headers,
        json={
            "title": "Backend Engineer 지원동기",
            "document_type": "MOTIVATION",
            "job_id": job_id,
            "question": "우리 회사에 지원한 이유를 작성해 주세요.",
            "instructions": "공고와 사용자 입력 근거만 사용하세요.",
            "tone": "PROFESSIONAL",
            "character_limit": 1000,
            "focus_points": ["FastAPI", "PostgreSQL"],
        },
    )
    assert response.status_code == 201
    return int(response.json()["data"]["id"])


def test_document_crud_and_mock_generation(client: TestClient):
    headers = auth_headers(client)
    job_id = create_job(client, headers)
    document_id = create_document(client, headers, job_id)

    generate_response = client.post(f"/api/v1/documents/{document_id}/generate", headers=headers, json={})
    assert generate_response.status_code == 200
    generated = generate_response.json()["data"]
    assert generated["current_version_number"] == 1
    assert generated["current_version"]["is_ai_generated"] is True
    assert generated["current_version"]["character_count"] > 0
    assert generated["status"] in {"COMPLETED", "REVIEW_REQUIRED"}

    detail_response = client.get(f"/api/v1/documents/{document_id}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["current_version"]["content"]

    list_response = client.get("/api/v1/documents", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()["data"]["total"] == 1


def test_generated_document_has_sources_versions_and_runs(client: TestClient):
    headers = auth_headers(client)
    job_id = create_job(client, headers)
    document_id = create_document(client, headers, job_id)
    assert client.post(f"/api/v1/documents/{document_id}/generate", headers=headers, json={}).status_code == 200

    versions = client.get(f"/api/v1/documents/{document_id}/versions", headers=headers).json()["data"]
    sources = client.get(f"/api/v1/documents/{document_id}/sources", headers=headers).json()["data"]
    runs = client.get(f"/api/v1/documents/{document_id}/generation-runs", headers=headers).json()["data"]

    assert len(versions) == 1
    assert sources
    assert runs[0]["status"] == "COMPLETED"
    assert all(source["evidence"]["evidence_text"] for source in sources)


def test_user_edit_regenerate_and_restore_preserve_versions(client: TestClient):
    headers = auth_headers(client)
    job_id = create_job(client, headers)
    document_id = create_document(client, headers, job_id)
    assert client.post(f"/api/v1/documents/{document_id}/generate", headers=headers, json={}).status_code == 200

    edit_response = client.post(
        f"/api/v1/documents/{document_id}/versions",
        headers=headers,
        json={"content": "사용자가 확인한 근거만 남긴 편집본입니다.", "change_summary": "manual edit"},
    )
    assert edit_response.status_code == 201
    assert edit_response.json()["data"]["version_number"] == 2

    regen_response = client.post(f"/api/v1/documents/{document_id}/regenerate", headers=headers, json={})
    assert regen_response.status_code == 200
    assert regen_response.json()["data"]["current_version_number"] == 3

    restore_response = client.post(
        f"/api/v1/documents/{document_id}/versions/{edit_response.json()['data']['id']}/restore",
        headers=headers,
    )
    assert restore_response.status_code == 200
    assert restore_response.json()["data"]["version_number"] == 4


def test_duplicate_and_archive_document(client: TestClient):
    headers = auth_headers(client)
    document_id = create_document(client, headers)
    assert client.post(f"/api/v1/documents/{document_id}/generate", headers=headers, json={}).status_code == 200

    duplicate_response = client.post(f"/api/v1/documents/{document_id}/duplicate", headers=headers, json={})
    assert duplicate_response.status_code == 201
    assert duplicate_response.json()["data"]["current_version_number"] == 1

    archive_response = client.delete(f"/api/v1/documents/{document_id}", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["data"]["archived"] is True


def test_document_ownership_blocks_other_users(client: TestClient):
    first_headers = auth_headers(client, "first@example.com")
    document_id = create_document(client, first_headers)
    second_headers = auth_headers(client, "second@example.com")

    response = client.get(f"/api/v1/documents/{document_id}", headers=second_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


def test_document_provider_status(client: TestClient):
    headers = auth_headers(client)
    response = client.get("/api/v1/ai/document-providers", headers=headers)

    assert response.status_code == 200
    assert response.json()["data"]["active_provider"] == "mock"
