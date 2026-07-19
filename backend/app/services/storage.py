import hashlib
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from uuid import uuid4
from zipfile import BadZipFile, ZipFile

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import AppError

PDF_SIGNATURE = b"%PDF-"
DOCX_REQUIRED_MEMBERS = {"[Content_Types].xml", "word/document.xml"}
CHUNK_SIZE = 64 * 1024
RESERVED_EXTENSIONS = {
    ".bat",
    ".cmd",
    ".com",
    ".exe",
    ".js",
    ".msi",
    ".ps1",
    ".scr",
    ".sh",
    ".vbs",
}
CONTENT_TYPES_BY_EXTENSION = {
    ".pdf": {"application/pdf"},
    ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
}


@dataclass(frozen=True)
class StoredFile:
    original_filename: str
    stored_filename: str
    storage_path: str
    content_type: str
    file_extension: str
    file_size: int
    file_hash: str
    content: bytes


class LocalFileStorage:
    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = Path(base_dir or settings.resume_storage_dir).resolve()

    async def validate_and_read(self, upload: UploadFile) -> StoredFile:
        original_filename = self.validate_filename(upload.filename or "")
        extension = Path(original_filename).suffix.lower()
        self.validate_extension(original_filename, extension)
        content_type = self.validate_content_type(extension, upload.content_type)
        content, file_hash = await self.read_limited(upload)
        self.validate_signature_and_structure(extension, content)

        stored_filename = f"{uuid4().hex}{extension}"
        return StoredFile(
            original_filename=original_filename,
            stored_filename=stored_filename,
            storage_path=str(self.base_dir / stored_filename),
            content_type=content_type,
            file_extension=extension,
            file_size=len(content),
            file_hash=file_hash,
            content=content,
        )

    def validate_filename(self, filename: str) -> str:
        if not filename:
            raise AppError("RESUME_FILE_NAME_REQUIRED", "이력서 파일명이 필요합니다.", 422)
        if "\x00" in filename or any(ord(char) < 32 for char in filename):
            raise AppError("RESUME_FILE_NAME_INVALID", "이력서 파일명이 올바르지 않습니다.", 422)
        if "/" in filename or "\\" in filename:
            raise AppError("RESUME_FILE_NAME_INVALID", "이력서 파일명에 경로 구분자를 사용할 수 없습니다.", 422)
        original_filename = Path(filename).name
        if original_filename != filename:
            raise AppError("RESUME_FILE_NAME_INVALID", "이력서 파일명이 올바르지 않습니다.", 422)
        return original_filename

    def validate_extension(self, original_filename: str, extension: str) -> None:
        suffixes = [suffix.lower() for suffix in Path(original_filename).suffixes]
        if len(suffixes) > 1 and any(
            suffix in settings.resume_allowed_extensions or suffix in RESERVED_EXTENSIONS
            for suffix in suffixes
        ):
            raise AppError(
                "RESUME_FILE_DOUBLE_EXTENSION_NOT_ALLOWED",
                "다중 확장자 이력서 파일은 업로드할 수 없습니다.",
                422,
            )
        if extension not in settings.resume_allowed_extensions:
            raise AppError(
                "RESUME_FILE_EXTENSION_NOT_ALLOWED",
                "PDF 또는 DOCX 파일만 업로드할 수 있습니다.",
                422,
            )

    def validate_content_type(self, extension: str, upload_content_type: str | None) -> str:
        content_type = (upload_content_type or "application/octet-stream").lower()
        if content_type not in settings.resume_allowed_content_types:
            raise AppError(
                "RESUME_FILE_CONTENT_TYPE_NOT_ALLOWED",
                "허용되지 않는 이력서 파일 형식입니다.",
                422,
            )
        if content_type not in CONTENT_TYPES_BY_EXTENSION.get(extension, set()):
            raise AppError(
                "RESUME_FILE_CONTENT_TYPE_NOT_ALLOWED",
                "파일 확장자와 MIME 타입이 일치하지 않습니다.",
                422,
            )
        return content_type

    async def read_limited(self, upload: UploadFile) -> tuple[bytes, str]:
        content = bytearray()
        digest = hashlib.sha256()
        total = 0
        while True:
            chunk = await upload.read(CHUNK_SIZE)
            if not chunk:
                break
            total += len(chunk)
            if total > settings.resume_max_file_size_bytes:
                raise AppError("RESUME_FILE_TOO_LARGE", "이력서 파일 크기가 제한을 초과했습니다.", 413)
            digest.update(chunk)
            content.extend(chunk)
        if not content:
            raise AppError("RESUME_FILE_EMPTY", "빈 파일은 업로드할 수 없습니다.", 422)
        return bytes(content), digest.hexdigest()

    def validate_signature_and_structure(self, extension: str, content: bytes) -> None:
        if extension == ".pdf":
            if not content.startswith(PDF_SIGNATURE):
                raise AppError(
                    "RESUME_FILE_SIGNATURE_INVALID",
                    "PDF 파일 signature가 올바르지 않습니다.",
                    422,
                )
            return

        if extension == ".docx":
            try:
                with ZipFile(BytesIO(content)) as archive:
                    names = set(archive.namelist())
            except BadZipFile as exc:
                raise AppError(
                    "RESUME_FILE_STRUCTURE_INVALID",
                    "DOCX 파일 구조가 올바르지 않습니다.",
                    422,
                ) from exc
            if not DOCX_REQUIRED_MEMBERS.issubset(names):
                raise AppError(
                    "RESUME_FILE_STRUCTURE_INVALID",
                    "DOCX 필수 내부 파일이 없습니다.",
                    422,
                )

    def save(self, stored: StoredFile) -> None:
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            path = self.resolve_storage_path(stored.storage_path)
            path.write_bytes(stored.content)
        except AppError:
            raise
        except OSError as exc:
            raise AppError("RESUME_FILE_STORAGE_FAILED", "이력서 파일 저장에 실패했습니다.", 500) from exc

    def resolve_storage_path(self, storage_path: str) -> Path:
        path = Path(storage_path).resolve()
        if path.parent != self.base_dir:
            raise AppError("RESUME_FILE_STORAGE_PATH_INVALID", "이력서 파일 저장 경로가 올바르지 않습니다.", 500)
        return path

    def existing_file_path(self, storage_path: str) -> Path:
        path = self.resolve_storage_path(storage_path)
        if not path.exists() or not path.is_file():
            raise AppError("RESUME_FILE_MISSING_ON_STORAGE", "저장소에서 이력서 파일을 찾을 수 없습니다.", 404)
        return path

    def delete(self, storage_path: str, *, missing_ok: bool = True) -> bool:
        try:
            path = self.resolve_storage_path(storage_path)
            if not path.exists():
                return False
            path.unlink()
            return True
        except AppError:
            if missing_ok:
                return False
            raise
        except OSError as exc:
            raise AppError("RESUME_FILE_DELETE_FAILED", "이력서 파일 삭제에 실패했습니다.", 500) from exc
