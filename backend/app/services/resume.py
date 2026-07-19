import re
from io import BytesIO
from math import ceil
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.security import utc_now
from app.models.resume import Resume, ResumeExtractionStatus, ResumeFile, ResumeFileExtraction
from app.repositories.resume import ResumeRepository
from app.schemas.resume import ResumeCreate, ResumeListData, ResumePublic, ResumeUpdate
from app.services.storage import LocalFileStorage

RESUME_EXTRACTION_PARSER_VERSION = "v0.3.1-basic"
PDF_TEXT_PATTERN = re.compile(r"\((.*?)\)\s*Tj", re.DOTALL)


class ResumeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ResumeRepository(session)
        self.storage = LocalFileStorage()

    async def create_resume(self, user_id: int, payload: ResumeCreate) -> Resume:
        if payload.is_default:
            await self.repository.clear_default(user_id)
        resume = Resume(user_id=user_id, **payload.model_dump())
        self.session.add(resume)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise AppError("RESUME_DEFAULT_CONFLICT", "기본 이력서 설정이 충돌했습니다.", 409) from exc
        return await self.get_resume(user_id, resume.id)

    async def list_resumes(self, user_id: int, page: int, size: int) -> ResumeListData:
        resumes, total = await self.repository.list_resumes(user_id, page, size)
        return ResumeListData(
            items=[ResumePublic.model_validate(resume) for resume in resumes],
            page=page,
            size=size,
            total=total,
            total_pages=ceil(total / size) if total else 0,
        )

    async def get_resume(self, user_id: int, resume_id: int) -> Resume:
        resume = await self.repository.get_resume(user_id, resume_id)
        if not resume:
            raise AppError("RESUME_NOT_FOUND", "이력서를 찾을 수 없습니다.", 404)
        return resume

    async def update_resume(self, user_id: int, resume_id: int, payload: ResumeUpdate) -> Resume:
        resume = await self.get_resume(user_id, resume_id)
        data = payload.model_dump(exclude_unset=True)
        if data.get("is_default") is True:
            await self.repository.clear_default(user_id)
        for key, value in data.items():
            setattr(resume, key, value)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise AppError("RESUME_DEFAULT_CONFLICT", "기본 이력서 설정이 충돌했습니다.", 409) from exc
        return await self.get_resume(user_id, resume_id)

    async def set_default(self, user_id: int, resume_id: int) -> Resume:
        resume = await self.get_resume(user_id, resume_id)
        await self.repository.clear_default(user_id)
        resume.is_default = True
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise AppError("RESUME_DEFAULT_CONFLICT", "기본 이력서 설정이 충돌했습니다.", 409) from exc
        return await self.get_resume(user_id, resume_id)

    async def delete_resume(self, user_id: int, resume_id: int) -> None:
        resume = await self.get_resume(user_id, resume_id)
        paths = [file.storage_path for file in resume.files]
        await self.session.delete(resume)
        await self.session.commit()
        for path in paths:
            self.storage.delete(path)

    async def upload_file(self, user_id: int, resume_id: int, upload: UploadFile) -> ResumeFile:
        await self.get_resume(user_id, resume_id)
        stored = await self.storage.validate_and_read(upload)
        duplicate = await self.repository.get_duplicate_file_hash(user_id, stored.file_hash)
        if duplicate:
            raise AppError("RESUME_FILE_ALREADY_EXISTS", "이미 업로드한 이력서 파일입니다.", 409)

        self.storage.save(stored)
        resume_file = ResumeFile(
            resume_id=resume_id,
            user_id=user_id,
            original_filename=stored.original_filename,
            stored_filename=stored.stored_filename,
            storage_path=stored.storage_path,
            content_type=stored.content_type,
            file_extension=stored.file_extension,
            file_size=stored.file_size,
            file_hash=stored.file_hash,
            uploaded_at=utc_now(),
        )
        self.session.add(resume_file)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            self.storage.delete(stored.storage_path)
            raise AppError("RESUME_FILE_ALREADY_EXISTS", "이미 업로드한 이력서 파일입니다.", 409) from exc
        except Exception:
            await self.session.rollback()
            self.storage.delete(stored.storage_path)
            raise
        await self.session.refresh(resume_file)
        return resume_file

    async def get_file(self, user_id: int, resume_id: int, file_id: int) -> ResumeFile:
        resume_file = await self.repository.get_file(user_id, resume_id, file_id)
        if not resume_file:
            raise AppError("RESUME_FILE_NOT_FOUND", "이력서 파일을 찾을 수 없습니다.", 404)
        return resume_file

    async def delete_file(self, user_id: int, resume_id: int, file_id: int) -> None:
        resume_file = await self.get_file(user_id, resume_id, file_id)
        storage_path = resume_file.storage_path
        self.storage.delete(storage_path, missing_ok=True)
        await self.session.delete(resume_file)
        await self.session.commit()

    async def extract_file(self, user_id: int, resume_id: int, file_id: int) -> ResumeFileExtraction:
        resume_file = await self.get_file(user_id, resume_id, file_id)
        path = self.storage.existing_file_path(resume_file.storage_path)
        content = path.read_bytes()
        try:
            extracted_text = self.extract_text(resume_file.file_extension, content)
            if not extracted_text:
                raise AppError("RESUME_EXTRACTION_TEXT_EMPTY", "추출된 이력서 텍스트가 없습니다.", 422)
            return await self.upsert_extraction(
                user_id=user_id,
                resume_file=resume_file,
                status=ResumeExtractionStatus.COMPLETED,
                extracted_text=extracted_text,
                error_code=None,
                error_message=None,
            )
        except AppError as exc:
            if exc.code == "RESUME_FILE_MISSING_ON_STORAGE":
                raise
            return await self.upsert_extraction(
                user_id=user_id,
                resume_file=resume_file,
                status=ResumeExtractionStatus.FAILED,
                extracted_text=None,
                error_code=exc.code,
                error_message=exc.message,
            )

    async def get_extraction(self, user_id: int, resume_id: int, file_id: int) -> ResumeFileExtraction:
        resume_file = await self.get_file(user_id, resume_id, file_id)
        extraction = await self.repository.get_extraction(user_id, resume_file.id)
        if not extraction:
            raise AppError("RESUME_EXTRACTION_NOT_FOUND", "이력서 텍스트 추출 결과를 찾을 수 없습니다.", 404)
        return extraction

    async def upsert_extraction(
        self,
        *,
        user_id: int,
        resume_file: ResumeFile,
        status: ResumeExtractionStatus,
        extracted_text: str | None,
        error_code: str | None,
        error_message: str | None,
    ) -> ResumeFileExtraction:
        extraction = await self.repository.get_extraction(user_id, resume_file.id)
        if extraction is None:
            extraction = ResumeFileExtraction(
                resume_file_id=resume_file.id,
                user_id=user_id,
                status=status,
                parser_version=RESUME_EXTRACTION_PARSER_VERSION,
                source_file_hash=resume_file.file_hash,
                extracted_at=utc_now(),
            )
            self.session.add(extraction)
        extraction.status = status
        extraction.extracted_text = extracted_text
        extraction.text_length = len(extracted_text or "")
        extraction.parser_version = RESUME_EXTRACTION_PARSER_VERSION
        extraction.source_file_hash = resume_file.file_hash
        extraction.error_code = error_code
        extraction.error_message = error_message
        extraction.extracted_at = utc_now()
        await self.session.commit()
        await self.session.refresh(extraction)
        return extraction

    def extract_text(self, extension: str, content: bytes) -> str:
        if extension == ".docx":
            return self.extract_docx_text(content)
        if extension == ".pdf":
            return self.extract_pdf_text(content)
        raise AppError("RESUME_EXTRACTION_UNSUPPORTED_FILE_TYPE", "지원하지 않는 이력서 추출 파일 형식입니다.", 422)

    def extract_docx_text(self, content: bytes) -> str:
        try:
            with ZipFile(BytesIO(content)) as archive:
                document_xml = archive.read("word/document.xml")
        except (BadZipFile, KeyError) as exc:
            raise AppError("RESUME_EXTRACTION_FAILED", "DOCX 텍스트 추출에 실패했습니다.", 422) from exc
        try:
            root = ElementTree.fromstring(document_xml)
        except ElementTree.ParseError as exc:
            raise AppError("RESUME_EXTRACTION_FAILED", "DOCX XML 파싱에 실패했습니다.", 422) from exc
        texts = [
            node.text.strip()
            for node in root.iter()
            if node.tag.rsplit("}", 1)[-1] == "t" and node.text and node.text.strip()
        ]
        return "\n".join(texts).strip()

    def extract_pdf_text(self, content: bytes) -> str:
        raw_text = content.decode("latin-1", errors="ignore")
        matches = [self.clean_pdf_literal(match) for match in PDF_TEXT_PATTERN.findall(raw_text)]
        text = "\n".join(match for match in matches if match).strip()
        if text:
            return text
        visible = "".join(char if 32 <= ord(char) <= 126 or char in "\r\n\t" else " " for char in raw_text)
        return re.sub(r"\s+", " ", visible.replace("%PDF-", " ")).strip()

    def clean_pdf_literal(self, value: str) -> str:
        return (
            value.replace(r"\(", "(")
            .replace(r"\)", ")")
            .replace(r"\\", "\\")
            .replace(r"\n", "\n")
            .strip()
        )
