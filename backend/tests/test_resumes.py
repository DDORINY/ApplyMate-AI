from __future__ import annotations

# ruff: noqa: F811

import shutil
from uuid import uuid4
from pathlib import Path

import pytest

from test_auth import client, login, signup  # noqa: F401
from app.services.storage import LocalFileStorage


def auth_headers(client, email: str = "resumes@example.com") -> dict[str, str]:
    signup_response = signup(client, email=email)
    assert signup_response.status_code == 201, signup_response.json()
    response = login(client, email=email)
    assert response.status_code == 200, response.json()
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


@pytest.fixture()
def resume_storage(monkeypatch):
    from app.services import resume as resume_service_module

    storage_root = Path.cwd() / ".test-storage" / uuid4().hex
    monkeypatch.setattr(
        resume_service_module,
        "LocalFileStorage",
        lambda: LocalFileStorage(str(storage_root)),
    )
    yield storage_root
    if storage_root.exists():
        shutil.rmtree(storage_root)


def create_resume(client, headers, **overrides):
    payload = {"title": "Backend Resume", "description": "Main resume"}
    payload.update(overrides)
    response = client.post("/api/v1/resumes", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()["data"]


def pdf_file(name: str = "resume.pdf", content: bytes = b"%PDF-1.4\nresume"):
    return {"file": (name, content, "application/pdf")}


def test_resume_requires_auth(client):
    response = client.get("/api/v1/resumes")

    assert response.status_code == 401


def test_create_list_update_set_default_and_delete_resume(client, resume_storage):
    headers = auth_headers(client)
    first = create_resume(client, headers, title="First", is_default=True)
    second = create_resume(client, headers, title="Second")

    list_response = client.get("/api/v1/resumes", headers=headers)
    update_response = client.patch(
        f"/api/v1/resumes/{second['id']}",
        json={"description": "Updated", "is_default": True},
        headers=headers,
    )
    first_detail = client.get(f"/api/v1/resumes/{first['id']}", headers=headers)
    delete_response = client.delete(f"/api/v1/resumes/{second['id']}", headers=headers)

    assert list_response.status_code == 200
    assert list_response.json()["data"]["total"] == 2
    assert update_response.status_code == 200
    assert update_response.json()["data"]["description"] == "Updated"
    assert update_response.json()["data"]["is_default"] is True
    assert first_detail.json()["data"]["is_default"] is False
    assert delete_response.status_code == 200


def test_resume_ownership_is_enforced(client, resume_storage):
    first_headers = auth_headers(client, email="resume-owner@example.com")
    resume = create_resume(client, first_headers)
    client.cookies.clear()
    other_headers = auth_headers(client, email="resume-other@example.com")

    response = client.get(f"/api/v1/resumes/{resume['id']}", headers=other_headers)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESUME_NOT_FOUND"


def test_upload_download_and_delete_resume_file(client, resume_storage):
    headers = auth_headers(client)
    resume = create_resume(client, headers)

    upload = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=pdf_file(),
        headers=headers,
    )
    file_data = upload.json()["data"]
    stored_files = list(Path(resume_storage).iterdir())
    download = client.get(
        f"/api/v1/resumes/{resume['id']}/files/{file_data['id']}/download",
        headers=headers,
    )
    delete_response = client.delete(
        f"/api/v1/resumes/{resume['id']}/files/{file_data['id']}",
        headers=headers,
    )

    assert upload.status_code == 201
    assert file_data["original_filename"] == "resume.pdf"
    assert file_data["file_extension"] == ".pdf"
    assert len(stored_files) == 1
    assert download.status_code == 200
    assert download.content.startswith(b"%PDF")
    assert delete_response.status_code == 200
    assert not stored_files[0].exists()


def test_upload_rejects_duplicate_file_hash(client, resume_storage):
    headers = auth_headers(client)
    resume = create_resume(client, headers)
    assert (
        client.post(f"/api/v1/resumes/{resume['id']}/files", files=pdf_file(), headers=headers).status_code
        == 201
    )

    response = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=pdf_file(name="copy.pdf"),
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "RESUME_FILE_ALREADY_EXISTS"


def test_upload_rejects_invalid_extension_and_content_type(client, resume_storage):
    headers = auth_headers(client)
    resume = create_resume(client, headers)

    bad_extension = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files={"file": ("resume.exe", b"binary", "application/octet-stream")},
        headers=headers,
    )
    bad_content_type = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files={"file": ("resume.pdf", b"%PDF", "text/plain")},
        headers=headers,
    )

    assert bad_extension.status_code == 422
    assert bad_extension.json()["error"]["code"] == "RESUME_FILE_EXTENSION_NOT_ALLOWED"
    assert bad_content_type.status_code == 422
    assert bad_content_type.json()["error"]["code"] == "RESUME_FILE_CONTENT_TYPE_NOT_ALLOWED"


def test_upload_rejects_large_file(client, resume_storage):
    headers = auth_headers(client)
    resume = create_resume(client, headers)

    response = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=pdf_file(content=b"x" * 5_242_881),
        headers=headers,
    )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "RESUME_FILE_TOO_LARGE"
