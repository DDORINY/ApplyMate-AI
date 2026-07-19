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
from app.models.resume import Resume, ResumeExtractionRun, ResumeExtractionStatus, ResumeFile, ResumeFileExtraction
from app.repositories.resume import ResumeRepository
from app.schemas.resume import ResumeCreate, ResumeExtractionUpdate, ResumeListData, ResumePublic, ResumeUpdate
from app.services.storage import LocalFileStorage

RESUME_EXTRACTION_PARSER_VERSION = "v0.3.1-basic"
RESUME_EXTRACTION_EXTRACTOR = "applymate-basic-parser"
PDF_TEXT_PATTERN = re.compile(r"\((.*?)\)\s*Tj", re.DOTALL)
PDF_PAGE_SPLIT_PATTERN = re.compile(r"/Type\s*/Page\b")
SECTION_KEYWORDS = {
    "SUMMARY": ("summary", "소개", "요약", "profile"),
    "SKILLS": ("skills", "기술", "스킬", "tech"),
    "EXPERIENCE": ("experience", "경력", "work"),
    "PROJECTS": ("projects", "프로젝트"),
    "EDUCATION": ("education", "학력", "교육"),
    "CERTIFICATIONS": ("certification", "certificate", "자격증"),
    "AWARDS": ("awards", "수상"),
    "CONTACT": ("contact", "email", "phone", "연락처"),
    "PORTFOLIO": ("portfolio", "github", "blog", "포트폴리오"),
}


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
        extraction = await self.prepare_extraction(user_id, resume_file)
        run = await self.start_extraction_run(user_id, resume_file, extraction)

        path = self.storage.existing_file_path(resume_file.storage_path)
        content = path.read_bytes()
        try:
            result = self.extract_text(resume_file.file_extension, content)
            return await self.complete_extraction(
                extraction=extraction,
                run=run,
                status=ResumeExtractionStatus.COMPLETED,
                raw_text=str(result["raw_text"]),
                page_texts=list(result["page_texts"]),
                section_candidates=self.detect_sections(str(result["raw_text"])),
                error_code=None,
                error_message=None,
            )
        except AppError as exc:
            if exc.code == "RESUME_FILE_MISSING_ON_STORAGE":
                raise
            return await self.complete_extraction(
                extraction=extraction,
                run=run,
                status=self.status_for_extraction_error(exc.code),
                raw_text=None,
                page_texts=[],
                section_candidates=[],
                error_code=exc.code,
                error_message=exc.message,
            )

    async def prepare_extraction(self, user_id: int, resume_file: ResumeFile) -> ResumeFileExtraction:
        extraction = await self.repository.get_extraction(user_id, resume_file.id)
        if extraction and extraction.extraction_status == ResumeExtractionStatus.PROCESSING:
            raise AppError("RESUME_EXTRACTION_ALREADY_PROCESSING", "이력서 텍스트 추출이 이미 진행 중입니다.", 409)
        if extraction is None:
            extraction = ResumeFileExtraction(
                resume_file_id=resume_file.id,
                user_id=user_id,
                extraction_status=ResumeExtractionStatus.PENDING,
                page_texts=[],
                section_candidates=[],
                input_hash=resume_file.file_hash,
                extracted_at=utc_now(),
            )
            self.session.add(extraction)
            await self.session.flush()
        return extraction

    async def start_extraction_run(
        self,
        user_id: int,
        resume_file: ResumeFile,
        extraction: ResumeFileExtraction,
    ) -> ResumeExtractionRun:
        run = ResumeExtractionRun(
            extraction_id=extraction.id,
            resume_file_id=resume_file.id,
            user_id=user_id,
            status=ResumeExtractionStatus.PROCESSING,
            input_hash=resume_file.file_hash,
            extractor=RESUME_EXTRACTION_EXTRACTOR,
            extractor_version=RESUME_EXTRACTION_PARSER_VERSION,
            started_at=utc_now(),
            metadata_json={},
        )
        self.session.add(run)
        await self.session.flush()
        extraction.extraction_status = ResumeExtractionStatus.PROCESSING
        extraction.current_run_id = run.id
        extraction.input_hash = resume_file.file_hash
        extraction.is_outdated = False
        await self.session.commit()
        await self.session.refresh(run)
        await self.session.refresh(extraction)
        return run

    async def get_extraction(self, user_id: int, resume_id: int, file_id: int) -> ResumeFileExtraction:
        resume_file = await self.get_file(user_id, resume_id, file_id)
        extraction = await self.repository.get_extraction(user_id, resume_file.id)
        if not extraction:
            raise AppError("RESUME_EXTRACTION_NOT_FOUND", "이력서 텍스트 추출 결과를 찾을 수 없습니다.", 404)
        extraction.is_outdated = extraction.input_hash != resume_file.file_hash
        return extraction

    async def update_extraction(
        self,
        user_id: int,
        resume_id: int,
        file_id: int,
        payload: ResumeExtractionUpdate,
    ) -> ResumeFileExtraction:
        resume_file = await self.get_file(user_id, resume_id, file_id)
        extraction = await self.repository.get_extraction(user_id, resume_file.id)
        if not extraction:
            raise AppError("RESUME_EXTRACTION_NOT_FOUND", "이력서 텍스트 추출 결과를 찾을 수 없습니다.", 404)
        if extraction.extraction_status not in {ResumeExtractionStatus.COMPLETED, ResumeExtractionStatus.TEXT_NOT_FOUND}:
            raise AppError("RESUME_EXTRACTION_NOT_EDITABLE", "수정할 수 없는 이력서 추출 상태입니다.", 409)
        extraction.edited_text = payload.edited_text
        extraction.character_count = len(payload.edited_text)
        extraction.is_user_edited = True
        extraction.is_outdated = extraction.input_hash != resume_file.file_hash
        await self.session.commit()
        await self.session.refresh(extraction)
        return extraction

    async def list_extraction_runs(self, user_id: int, resume_id: int, file_id: int) -> list[ResumeExtractionRun]:
        resume_file = await self.get_file(user_id, resume_id, file_id)
        return await self.repository.list_extraction_runs(user_id, resume_file.id)

    async def get_extraction_run(
        self,
        user_id: int,
        resume_id: int,
        file_id: int,
        run_id: int,
    ) -> ResumeExtractionRun:
        resume_file = await self.get_file(user_id, resume_id, file_id)
        run = await self.repository.get_extraction_run(user_id, resume_file.id, run_id)
        if not run:
            raise AppError("RESUME_EXTRACTION_RUN_NOT_FOUND", "이력서 텍스트 추출 실행 이력을 찾을 수 없습니다.", 404)
        return run

    async def complete_extraction(
        self,
        *,
        extraction: ResumeFileExtraction,
        run: ResumeExtractionRun,
        status: ResumeExtractionStatus,
        raw_text: str | None,
        page_texts: list[dict[str, object]],
        section_candidates: list[dict[str, object]],
        error_code: str | None,
        error_message: str | None,
    ) -> ResumeFileExtraction:
        now = utc_now()
        extraction.extraction_status = status
        extraction.raw_text = raw_text
        extraction.page_texts = page_texts
        extraction.section_candidates = section_candidates
        extraction.page_count = len(page_texts)
        extraction.character_count = len(raw_text or "")
        extraction.error_code = error_code
        extraction.error_message = error_message
        extraction.extracted_at = now
        extraction.current_run_id = run.id
        run.status = status
        run.completed_at = now
        run.error_code = error_code
        run.error_message = error_message
        run.page_count = extraction.page_count
        run.character_count = extraction.character_count
        run.metadata_json = {
            "page_texts": page_texts,
            "section_candidates": section_candidates,
            "ocr_excluded": True,
        }
        await self.session.commit()
        await self.session.refresh(extraction)
        return extraction

    def extract_text(self, extension: str, content: bytes) -> dict[str, object]:
        if extension == ".docx":
            return self.extract_docx_text(content)
        if extension == ".pdf":
            return self.extract_pdf_text(content)
        raise AppError("RESUME_EXTRACTION_UNSUPPORTED_FILE_TYPE", "지원하지 않는 이력서 추출 파일 형식입니다.", 422)

    def extract_docx_text(self, content: bytes) -> dict[str, object]:
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
        raw_text = "\n".join(texts).strip()
        if not raw_text:
            raise AppError("RESUME_EXTRACTION_TEXT_NOT_FOUND", "DOCX에서 추출 가능한 텍스트를 찾지 못했습니다.", 422)
        return {"raw_text": raw_text, "page_texts": [{"page": 1, "text": raw_text, "page_break_supported": False}]}

    def extract_pdf_text(self, content: bytes) -> dict[str, object]:
        if b"/Encrypt" in content[:4096] or b"/Encrypt" in content[-4096:]:
            raise AppError("RESUME_EXTRACTION_PDF_ENCRYPTED", "암호화된 PDF는 텍스트를 추출할 수 없습니다.", 422)
        raw_text = content.decode("latin-1", errors="ignore")
        matches = [self.clean_pdf_literal(match) for match in PDF_TEXT_PATTERN.findall(raw_text)]
        text = "\n".join(match for match in matches if match).strip()
        if not matches:
            raise AppError("RESUME_EXTRACTION_OCR_REQUIRED", "텍스트 레이어가 없는 PDF입니다. OCR이 필요합니다.", 422)
        if not text:
            raise AppError("RESUME_EXTRACTION_TEXT_NOT_FOUND", "PDF에서 추출 가능한 텍스트를 찾지 못했습니다.", 422)
        page_count = max(1, len(PDF_PAGE_SPLIT_PATTERN.findall(raw_text)))
        return {"raw_text": text, "page_texts": self.split_text_into_pages(text, page_count)}

    def split_text_into_pages(self, text: str, page_count: int) -> list[dict[str, object]]:
        if page_count <= 1:
            return [{"page": 1, "text": text}]
        lines = [line for line in text.splitlines() if line.strip()]
        if not lines:
            return [{"page": page, "text": ""} for page in range(1, page_count + 1)]
        chunk_size = max(1, ceil(len(lines) / page_count))
        return [
            {"page": page + 1, "text": "\n".join(lines[page * chunk_size : (page + 1) * chunk_size]).strip()}
            for page in range(page_count)
        ]

    def detect_sections(self, text: str) -> list[dict[str, object]]:
        lowered = text.lower()
        candidates = []
        for section, keywords in SECTION_KEYWORDS.items():
            if any(keyword.lower() in lowered for keyword in keywords):
                candidates.append({"section": section, "confidence": 0.5, "text": section})
        if not candidates:
            candidates.append({"section": "UNKNOWN", "confidence": 0.1, "text": "UNKNOWN"})
        return candidates

    def status_for_extraction_error(self, code: str) -> ResumeExtractionStatus:
        if code == "RESUME_EXTRACTION_TEXT_NOT_FOUND":
            return ResumeExtractionStatus.TEXT_NOT_FOUND
        if code == "RESUME_EXTRACTION_OCR_REQUIRED":
            return ResumeExtractionStatus.OCR_REQUIRED
        return ResumeExtractionStatus.FAILED

    def clean_pdf_literal(self, value: str) -> str:
        return (
            value.replace(r"\(", "(")
            .replace(r"\)", ")")
            .replace(r"\\", "\\")
            .replace(r"\n", "\n")
            .strip()
        )
