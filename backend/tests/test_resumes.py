from __future__ import annotations

# ruff: noqa: F811

import shutil
from io import BytesIO
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

import pytest

from app.services.storage import LocalFileStorage

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


def docx_bytes() -> bytes:
    output = BytesIO()
    with ZipFile(output, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr(
            "word/document.xml",
            (
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                "<w:body><w:p><w:r><w:t>ApplyMate DOCX Resume</w:t></w:r></w:p></w:body>"
                "</w:document>"
            ),
        )
    return output.getvalue()


def docx_file(name: str = "resume.docx", content: bytes | None = None):
    return {
        "file": (
            name,
            content if content is not None else docx_bytes(),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }


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


def test_upload_accepts_valid_docx(client, resume_storage):
    headers = auth_headers(client)
    resume = create_resume(client, headers)

    response = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=docx_file(),
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["data"]["file_extension"] == ".docx"


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


def test_same_file_hash_is_allowed_for_other_user(client, resume_storage):
    first_headers = auth_headers(client, email="hash-owner@example.com")
    first_resume = create_resume(client, first_headers)
    assert (
        client.post(
            f"/api/v1/resumes/{first_resume['id']}/files",
            files=pdf_file(),
            headers=first_headers,
        ).status_code
        == 201
    )
    client.cookies.clear()
    other_headers = auth_headers(client, email="hash-other@example.com")
    other_resume = create_resume(client, other_headers)

    response = client.post(
        f"/api/v1/resumes/{other_resume['id']}/files",
        files=pdf_file(),
        headers=other_headers,
    )

    assert response.status_code == 201


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


def test_upload_rejects_signature_and_structure_mismatch(client, resume_storage):
    headers = auth_headers(client)
    resume = create_resume(client, headers)

    fake_pdf = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=pdf_file(content=b"not a pdf"),
        headers=headers,
    )
    fake_docx = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=docx_file(content=b"not a zip"),
        headers=headers,
    )
    zip_not_docx = BytesIO()
    with ZipFile(zip_not_docx, "w") as archive:
        archive.writestr("hello.txt", "not docx")
    generic_zip = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=docx_file(name="zip.docx", content=zip_not_docx.getvalue()),
        headers=headers,
    )

    assert fake_pdf.status_code == 422
    assert fake_pdf.json()["error"]["code"] == "RESUME_FILE_SIGNATURE_INVALID"
    assert fake_docx.status_code == 422
    assert fake_docx.json()["error"]["code"] == "RESUME_FILE_STRUCTURE_INVALID"
    assert generic_zip.status_code == 422
    assert generic_zip.json()["error"]["code"] == "RESUME_FILE_STRUCTURE_INVALID"


def test_upload_rejects_double_extension_and_path_filename(client, resume_storage):
    headers = auth_headers(client)
    resume = create_resume(client, headers)

    double_extension = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=pdf_file(name="resume.pdf.exe"),
        headers=headers,
    )
    path_filename = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=pdf_file(name="../resume.pdf"),
        headers=headers,
    )

    assert double_extension.status_code == 422
    assert double_extension.json()["error"]["code"] == "RESUME_FILE_DOUBLE_EXTENSION_NOT_ALLOWED"
    assert path_filename.status_code == 422
    assert path_filename.json()["error"]["code"] == "RESUME_FILE_NAME_INVALID"


@pytest.mark.parametrize("filename", ["resume\x00.pdf", "resume\x1f.pdf"])
def test_storage_rejects_null_or_control_character_filename(resume_storage, filename):
    storage = LocalFileStorage(resume_storage)

    with pytest.raises(Exception) as exc_info:
        storage.validate_filename(filename)

    assert getattr(exc_info.value, "code", None) == "RESUME_FILE_NAME_INVALID"


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


def test_download_returns_error_when_storage_file_is_missing(client, resume_storage):
    headers = auth_headers(client)
    resume = create_resume(client, headers)
    upload = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=pdf_file(),
        headers=headers,
    )
    file_data = upload.json()["data"]
    for stored_file in Path(resume_storage).iterdir():
        stored_file.unlink()

    response = client.get(
        f"/api/v1/resumes/{resume['id']}/files/{file_data['id']}/download",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESUME_FILE_MISSING_ON_STORAGE"


def test_extract_docx_resume_text(client, resume_storage):
    headers = auth_headers(client)
    resume = create_resume(client, headers)
    upload = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=docx_file(),
        headers=headers,
    )
    file_id = upload.json()["data"]["id"]

    extract = client.post(
        f"/api/v1/resumes/{resume['id']}/files/{file_id}/extraction",
        headers=headers,
    )
    get_result = client.get(
        f"/api/v1/resumes/{resume['id']}/files/{file_id}/extraction",
        headers=headers,
    )

    assert extract.status_code == 200
    assert extract.json()["data"]["status"] == "COMPLETED"
    assert extract.json()["data"]["extracted_text"] == "ApplyMate DOCX Resume"
    assert extract.json()["data"]["raw_text"] == "ApplyMate DOCX Resume"
    assert extract.json()["data"]["page_texts"][0]["page"] == 1
    assert extract.json()["data"]["is_outdated"] is False
    assert get_result.status_code == 200
    assert get_result.json()["data"]["text_length"] == len("ApplyMate DOCX Resume")


def test_extract_pdf_resume_text(client, resume_storage):
    headers = auth_headers(client)
    resume = create_resume(client, headers)
    upload = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=pdf_file(content=b"%PDF-1.4\nBT (ApplyMate PDF Resume) Tj ET\n%%EOF"),
        headers=headers,
    )
    file_id = upload.json()["data"]["id"]

    response = client.post(
        f"/api/v1/resumes/{resume['id']}/files/{file_id}/extraction",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "COMPLETED"
    assert response.json()["data"]["extracted_text"] == "ApplyMate PDF Resume"


def test_extract_pdf_without_text_layer_requires_ocr(client, resume_storage):
    headers = auth_headers(client)
    resume = create_resume(client, headers)
    upload = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=pdf_file(content=b"%PDF-1.4\n/image-only\n%%EOF"),
        headers=headers,
    )
    file_id = upload.json()["data"]["id"]

    response = client.post(
        f"/api/v1/resumes/{resume['id']}/files/{file_id}/extraction",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "OCR_REQUIRED"
    assert response.json()["data"]["error_code"] == "RESUME_EXTRACTION_OCR_REQUIRED"


def test_update_extraction_preserves_raw_text_and_marks_user_edited(client, resume_storage):
    headers = auth_headers(client)
    resume = create_resume(client, headers)
    upload = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=pdf_file(content=b"%PDF-1.4\nBT (ApplyMate PDF Resume) Tj ET\n%%EOF"),
        headers=headers,
    )
    file_id = upload.json()["data"]["id"]
    client.post(f"/api/v1/resumes/{resume['id']}/files/{file_id}/extraction", headers=headers)

    response = client.patch(
        f"/api/v1/resumes/{resume['id']}/files/{file_id}/extraction",
        json={"edited_text": "Edited resume text"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["data"]["raw_text"] == "ApplyMate PDF Resume"
    assert response.json()["data"]["edited_text"] == "Edited resume text"
    assert response.json()["data"]["extracted_text"] == "Edited resume text"
    assert response.json()["data"]["is_user_edited"] is True


def test_retry_extraction_preserves_run_history(client, resume_storage):
    headers = auth_headers(client)
    resume = create_resume(client, headers)
    upload = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=pdf_file(content=b"%PDF-1.4\nBT (ApplyMate PDF Resume) Tj ET\n%%EOF"),
        headers=headers,
    )
    file_id = upload.json()["data"]["id"]

    first = client.post(f"/api/v1/resumes/{resume['id']}/files/{file_id}/extraction", headers=headers)
    retry = client.post(f"/api/v1/resumes/{resume['id']}/files/{file_id}/extraction/retry", headers=headers)
    runs = client.get(f"/api/v1/resumes/{resume['id']}/files/{file_id}/extraction/runs", headers=headers)

    assert first.status_code == 200
    assert retry.status_code == 200
    assert runs.status_code == 200
    assert len(runs.json()["data"]["items"]) == 2
    assert runs.json()["data"]["items"][0]["status"] == "COMPLETED"


def test_extraction_ownership_is_enforced(client, resume_storage):
    owner_headers = auth_headers(client, email="extract-owner@example.com")
    resume = create_resume(client, owner_headers)
    upload = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=pdf_file(content=b"%PDF-1.4\nBT (ApplyMate PDF Resume) Tj ET\n%%EOF"),
        headers=owner_headers,
    )
    file_id = upload.json()["data"]["id"]
    client.cookies.clear()
    other_headers = auth_headers(client, email="extract-other@example.com")

    response = client.post(
        f"/api/v1/resumes/{resume['id']}/files/{file_id}/extraction",
        headers=other_headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESUME_FILE_NOT_FOUND"


def test_get_extraction_requires_existing_result(client, resume_storage):
    headers = auth_headers(client)
    resume = create_resume(client, headers)
    upload = client.post(
        f"/api/v1/resumes/{resume['id']}/files",
        files=pdf_file(),
        headers=headers,
    )
    file_id = upload.json()["data"]["id"]

    response = client.get(
        f"/api/v1/resumes/{resume['id']}/files/{file_id}/extraction",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESUME_EXTRACTION_NOT_FOUND"
