# ruff: noqa: F811

import pytest

from app.core.config import get_settings

from test_auth import client  # noqa: F401
from test_resumes import auth_headers, create_resume, docx_file, pdf_file, resume_storage  # noqa: F401,F811


def enable_mock_ai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_ANALYSIS_PROMPT_VERSION", "v0.3.2")
    monkeypatch.setenv("AI_ANALYSIS_SCHEMA_VERSION", "v0.3.2")
    get_settings.cache_clear()


def upload_and_extract_resume(client, headers, resume_id: int, text: str = "Python FastAPI Docker PostgreSQL"):
    upload = client.post(
        f"/api/v1/resumes/{resume_id}/files",
        files=pdf_file(content=f"%PDF-1.4\nBT ({text}) Tj ET\n%%EOF".encode()),
        headers=headers,
    )
    assert upload.status_code == 201, upload.json()
    file_id = upload.json()["data"]["id"]
    extraction = client.post(f"/api/v1/resumes/{resume_id}/files/{file_id}/extraction", headers=headers)
    assert extraction.status_code == 200, extraction.json()
    assert extraction.json()["data"]["status"] == "COMPLETED"
    return file_id, extraction.json()["data"]


def test_analyze_resume_uses_extracted_text_and_persists_result(client, resume_storage, monkeypatch):
    enable_mock_ai(monkeypatch)
    headers = auth_headers(client, email="resume-analysis@example.com")
    resume = create_resume(client, headers)
    file_id, extraction = upload_and_extract_resume(client, headers, resume["id"])

    response = client.post(
        f"/api/v1/resumes/{resume['id']}/files/{file_id}/analysis",
        headers=headers,
    )
    get_response = client.get(
        f"/api/v1/resumes/{resume['id']}/files/{file_id}/analysis",
        headers=headers,
    )

    assert response.status_code == 200, response.json()
    data = response.json()["data"]
    assert data["status"] == "COMPLETED"
    assert data["provider"] == "mock"
    assert data["input_source"] == "RAW"
    assert data["extraction_id"] == extraction["id"]
    assert {skill["name"] for skill in data["structured_result"]["skills"]} >= {
        "Python",
        "FastAPI",
        "Docker",
        "PostgreSQL",
    }
    assert data["structured_result"]["skills"][0]["evidence"][0]["source_text"] in extraction["raw_text"]
    assert get_response.status_code == 200
    assert get_response.json()["data"]["is_outdated"] is False


def test_analyze_resume_prefers_edited_extraction_text(client, resume_storage, monkeypatch):
    enable_mock_ai(monkeypatch)
    headers = auth_headers(client, email="resume-analysis-edited@example.com")
    resume = create_resume(client, headers)
    file_id, _ = upload_and_extract_resume(client, headers, resume["id"], text="Python")
    edit = client.patch(
        f"/api/v1/resumes/{resume['id']}/files/{file_id}/extraction",
        json={"edited_text": "TypeScript React Next.js"},
        headers=headers,
    )
    assert edit.status_code == 200

    response = client.post(f"/api/v1/resumes/{resume['id']}/files/{file_id}/analysis", headers=headers)

    assert response.status_code == 200, response.json()
    data = response.json()["data"]
    assert data["input_source"] == "EDITED"
    assert {skill["name"] for skill in data["structured_result"]["skills"]} >= {
        "TypeScript",
        "React",
        "Next.js",
    }


def test_resume_analysis_blocks_until_extraction_is_ready(client, resume_storage, monkeypatch):
    enable_mock_ai(monkeypatch)
    headers = auth_headers(client, email="resume-analysis-no-extraction@example.com")
    resume = create_resume(client, headers)
    upload = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=docx_file(),
        headers=headers,
    )
    file_id = upload.json()["data"]["id"]

    response = client.post(f"/api/v1/resumes/{resume['id']}/files/{file_id}/analysis", headers=headers)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "RESUME_ANALYSIS_EXTRACTION_REQUIRED"


def test_resume_analysis_blocks_ocr_required_file(client, resume_storage, monkeypatch):
    enable_mock_ai(monkeypatch)
    headers = auth_headers(client, email="resume-analysis-ocr@example.com")
    resume = create_resume(client, headers)
    upload = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=pdf_file(content=b"%PDF-1.4\n/image-only\n%%EOF"),
        headers=headers,
    )
    file_id = upload.json()["data"]["id"]
    extraction = client.post(f"/api/v1/resumes/{resume['id']}/files/{file_id}/extraction", headers=headers)
    assert extraction.json()["data"]["status"] == "OCR_REQUIRED"

    response = client.post(f"/api/v1/resumes/{resume['id']}/files/{file_id}/analysis", headers=headers)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "RESUME_ANALYSIS_EXTRACTION_NOT_READY"


def test_resume_analysis_retry_runs_and_profile_candidates(client, resume_storage, monkeypatch):
    enable_mock_ai(monkeypatch)
    headers = auth_headers(client, email="resume-analysis-runs@example.com")
    resume = create_resume(client, headers)
    file_id, _ = upload_and_extract_resume(client, headers, resume["id"])

    first = client.post(f"/api/v1/resumes/{resume['id']}/files/{file_id}/analysis", headers=headers)
    retry = client.post(f"/api/v1/resumes/{resume['id']}/files/{file_id}/analysis/retry", headers=headers)
    runs = client.get(f"/api/v1/resumes/{resume['id']}/files/{file_id}/analysis/runs", headers=headers)
    candidates = client.get(
        f"/api/v1/resumes/{resume['id']}/files/{file_id}/analysis/profile-candidates",
        headers=headers,
    )

    assert first.status_code == 200
    assert retry.status_code == 200
    assert runs.status_code == 200
    assert runs.json()["data"]["total"] == 2
    assert candidates.status_code == 200
    assert candidates.json()["data"]["items"][0]["action"] in {"ADD", "DUPLICATE"}


def test_resume_analysis_update_preserves_ai_original(client, resume_storage, monkeypatch):
    enable_mock_ai(monkeypatch)
    headers = auth_headers(client, email="resume-analysis-update@example.com")
    resume = create_resume(client, headers)
    file_id, _ = upload_and_extract_resume(client, headers, resume["id"])
    analysis = client.post(f"/api/v1/resumes/{resume['id']}/files/{file_id}/analysis", headers=headers).json()["data"]
    edited = analysis["structured_result"].copy()
    edited["summary"] = "사용자가 확인한 이력서 요약"

    response = client.patch(
        f"/api/v1/resumes/{resume['id']}/files/{file_id}/analysis",
        json={"edited_result": edited},
        headers=headers,
    )

    assert response.status_code == 200, response.json()
    data = response.json()["data"]
    assert data["structured_result"]["summary"] == analysis["structured_result"]["summary"]
    assert data["edited_result"]["summary"] == "사용자가 확인한 이력서 요약"
    assert data["result"]["summary"] == "사용자가 확인한 이력서 요약"
    assert data["is_user_edited"] is True


def test_resume_analysis_ownership_is_enforced(client, resume_storage, monkeypatch):
    enable_mock_ai(monkeypatch)
    owner_headers = auth_headers(client, email="resume-analysis-owner@example.com")
    resume = create_resume(client, owner_headers)
    file_id, _ = upload_and_extract_resume(client, owner_headers, resume["id"])
    client.cookies.clear()
    other_headers = auth_headers(client, email="resume-analysis-other@example.com")

    response = client.post(
        f"/api/v1/resumes/{resume['id']}/files/{file_id}/analysis",
        headers=other_headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESUME_FILE_NOT_FOUND"
