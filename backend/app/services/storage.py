from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import AppError


@dataclass(frozen=True)
class StoredFile:
    original_filename: str
    stored_filename: str
    storage_path: str
    content_type: str
    file_extension: str
    file_size: int
    content: bytes


class LocalFileStorage:
    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = Path(base_dir or settings.resume_storage_dir).resolve()

    async def validate_and_read(self, upload: UploadFile) -> StoredFile:
        original_filename = Path(upload.filename or "").name
        if not original_filename:
            raise AppError("RESUME_FILE_NAME_REQUIRED", "이력서 파일명이 필요합니다.", 422)

        extension = Path(original_filename).suffix.lower()
        if extension not in settings.resume_allowed_extensions:
            raise AppError("RESUME_FILE_EXTENSION_NOT_ALLOWED", "PDF 또는 DOCX 파일만 업로드할 수 있습니다.", 422)

        content_type = (upload.content_type or "application/octet-stream").lower()
        if content_type not in settings.resume_allowed_content_types:
            raise AppError("RESUME_FILE_CONTENT_TYPE_NOT_ALLOWED", "허용되지 않는 이력서 파일 형식입니다.", 422)

        content = await upload.read()
        if len(content) > settings.resume_max_file_size_bytes:
            raise AppError("RESUME_FILE_TOO_LARGE", "이력서 파일 크기가 제한을 초과했습니다.", 413)
        if not content:
            raise AppError("RESUME_FILE_EMPTY", "빈 파일은 업로드할 수 없습니다.", 422)

        stored_filename = f"{uuid4().hex}{extension}"
        return StoredFile(
            original_filename=original_filename,
            stored_filename=stored_filename,
            storage_path=str(self.base_dir / stored_filename),
            content_type=content_type,
            file_extension=extension,
            file_size=len(content),
            content=content,
        )

    def save(self, stored: StoredFile) -> None:
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            path = Path(stored.storage_path).resolve()
            if self.base_dir not in path.parents:
                raise AppError("RESUME_FILE_STORAGE_FAILED", "이력서 파일 저장 경로가 올바르지 않습니다.", 500)
            path.write_bytes(stored.content)
        except AppError:
            raise
        except OSError as exc:
            raise AppError("RESUME_FILE_STORAGE_FAILED", "이력서 파일 저장에 실패했습니다.", 500) from exc

    def delete(self, storage_path: str) -> None:
        path = Path(storage_path).resolve()
        if self.base_dir in path.parents and path.exists():
            path.unlink()
