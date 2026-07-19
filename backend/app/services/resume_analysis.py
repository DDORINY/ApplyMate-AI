import hashlib
from math import ceil
from typing import Any

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers import get_ai_provider, provider_status
from app.ai.resume_analysis_prompt import SYSTEM_PROMPT, build_user_prompt
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.security import utc_now
from app.models.resume import (
    ResumeAnalysis,
    ResumeAnalysisRun,
    ResumeAnalysisStatus,
    ResumeExtractionStatus,
    ResumeFile,
    ResumeFileExtraction,
)
from app.repositories.profile import ProfileRepository
from app.repositories.resume import ResumeRepository
from app.repositories.resume_analysis import ResumeAnalysisRepository
from app.schemas.job_analysis import AIProviderStatusData
from app.schemas.resume_analysis import (
    ResumeAnalysisDeletedData,
    ResumeAnalysisPublic,
    ResumeAnalysisRunsData,
    ResumeAnalysisRunPublic,
    ResumeAnalysisStructuredData,
    ResumeAnalysisUpdate,
    ResumeProfileCandidate,
    ResumeProfileCandidateData,
)
from app.services.resume import ResumeService


RESUME_ANALYSIS_MIN_TEXT_LENGTH = 10


class ResumeAnalysisService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.resume_repository = ResumeRepository(session)
        self.repository = ResumeAnalysisRepository(session)
        self.profile_repository = ProfileRepository(session)

    def get_provider_status(self) -> AIProviderStatusData:
        return AIProviderStatusData.model_validate(provider_status(get_settings()))

    async def analyze_resume(
        self,
        user_id: int,
        resume_id: int,
        file_id: int,
        *,
        force: bool = False,
    ) -> ResumeAnalysisPublic:
        settings = get_settings()
        resume_file = await ResumeService(self.session).get_file(user_id, resume_id, file_id)
        extraction = await self._get_ready_extraction(user_id, resume_file)
        input_text, input_source = self._analysis_input(extraction)
        input_hash = self._input_hash(input_text, extraction.id)

        existing = await self.repository.get_analysis(user_id, resume_file.id)
        if existing and existing.status == ResumeAnalysisStatus.PROCESSING:
            raise AppError("RESUME_ANALYSIS_ALREADY_PROCESSING", "이력서 분석이 이미 진행 중입니다.", 409)
        if existing and existing.status == ResumeAnalysisStatus.COMPLETED and existing.input_hash == input_hash and not force:
            return self._public(existing, current_input_hash=input_hash)

        provider = get_ai_provider(settings)
        started_at = utc_now()
        analysis = existing or ResumeAnalysis(
            resume_id=resume_id,
            resume_file_id=resume_file.id,
            extraction_id=extraction.id,
            user_id=user_id,
            prompt_version=settings.ai_analysis_prompt_version,
            schema_version=settings.ai_analysis_schema_version,
            input_hash=input_hash,
            resume_file_hash=resume_file.file_hash,
            extraction_run_id=extraction.current_run_id,
            input_source=input_source,
            input_length=len(input_text),
            profile_candidates=[],
        )
        analysis.status = ResumeAnalysisStatus.PROCESSING
        analysis.provider = provider.provider
        analysis.model = provider.model
        analysis.error_code = None
        analysis.error_message = None
        analysis.is_outdated = False
        self.session.add(analysis)
        await self.session.flush()

        run = ResumeAnalysisRun(
            analysis_id=analysis.id,
            resume_id=resume_id,
            resume_file_id=resume_file.id,
            extraction_id=extraction.id,
            user_id=user_id,
            status=ResumeAnalysisStatus.PROCESSING,
            provider=provider.provider,
            model=provider.model,
            prompt_version=settings.ai_analysis_prompt_version,
            schema_version=settings.ai_analysis_schema_version,
            input_hash=input_hash,
            input_source=input_source,
            input_length=len(input_text),
            started_at=started_at,
            usage_metadata={},
            raw_response_metadata={},
        )
        self.session.add(run)
        await self.session.flush()
        analysis.latest_run_id = run.id
        await self.session.commit()
        await self.session.refresh(run)
        await self.session.refresh(analysis)

        try:
            result = await provider.analyze_resume(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=build_user_prompt(input_text, settings),
                response_schema=ResumeAnalysisStructuredData,
            )
            parsed = ResumeAnalysisStructuredData.model_validate(result.parsed_data)
            self._validate_evidence(parsed, input_text, extraction.id)
            now = utc_now()
            structured = parsed.model_dump(mode="json")
            analysis.status = ResumeAnalysisStatus.COMPLETED
            analysis.provider = result.provider
            analysis.model = result.model
            analysis.prompt_version = settings.ai_analysis_prompt_version
            analysis.schema_version = settings.ai_analysis_schema_version
            analysis.input_hash = input_hash
            analysis.resume_file_hash = resume_file.file_hash
            analysis.extraction_id = extraction.id
            analysis.extraction_run_id = extraction.current_run_id
            analysis.input_source = input_source
            analysis.input_length = len(input_text)
            analysis.summary = parsed.summary
            analysis.structured_result = structured
            analysis.profile_candidates = await self._build_profile_candidates(user_id, parsed)
            analysis.error_code = None
            analysis.error_message = None
            analysis.analyzed_at = now
            analysis.updated_at = now
            analysis.is_outdated = False
            analysis.is_user_edited = False if not existing else analysis.is_user_edited
            run.status = ResumeAnalysisStatus.COMPLETED
            run.completed_at = now
            run.result_snapshot = structured
            run.usage_metadata = {
                "prompt_tokens": result.prompt_tokens,
                "completion_tokens": result.completion_tokens,
                "total_tokens": result.total_tokens,
                "latency_ms": result.latency_ms,
            }
            run.raw_response_metadata = {
                "request_id": result.request_id,
                "raw_response_stored": bool(settings.ai_store_raw_response and result.raw_response),
            }
            await self.session.commit()
            await self.session.refresh(analysis)
            return self._public(analysis, current_input_hash=input_hash)
        except (AppError, ValidationError, ValueError) as exc:
            mapped_exc = self._normalize_error(exc)
            await self._mark_failed(analysis, run, mapped_exc)
            if isinstance(exc, AppError):
                raise mapped_exc
            raise AppError("RESUME_ANALYSIS_INVALID_OUTPUT", "이력서 분석 결과 구조가 올바르지 않습니다.", 502) from exc

    async def get_analysis(self, user_id: int, resume_id: int, file_id: int) -> ResumeAnalysisPublic:
        resume_file = await ResumeService(self.session).get_file(user_id, resume_id, file_id)
        extraction = await self._get_ready_extraction(user_id, resume_file)
        analysis = await self.repository.get_analysis(user_id, resume_file.id)
        if not analysis:
            raise AppError("RESUME_ANALYSIS_NOT_FOUND", "이력서 분석 결과를 찾을 수 없습니다.", 404)
        input_text, _ = self._analysis_input(extraction)
        return self._public(analysis, current_input_hash=self._input_hash(input_text, extraction.id))

    async def update_analysis(
        self,
        user_id: int,
        resume_id: int,
        file_id: int,
        payload: ResumeAnalysisUpdate,
    ) -> ResumeAnalysisPublic:
        resume_file = await ResumeService(self.session).get_file(user_id, resume_id, file_id)
        extraction = await self._get_ready_extraction(user_id, resume_file)
        analysis = await self.repository.get_analysis(user_id, resume_file.id)
        if not analysis:
            raise AppError("RESUME_ANALYSIS_NOT_FOUND", "이력서 분석 결과를 찾을 수 없습니다.", 404)
        try:
            parsed = ResumeAnalysisStructuredData.model_validate(payload.edited_result)
            input_text, _ = self._analysis_input(extraction)
            self._validate_evidence(parsed, input_text, extraction.id)
        except (ValidationError, ValueError) as exc:
            raise AppError("RESUME_ANALYSIS_INVALID_OUTPUT", "수정한 이력서 분석 결과 구조가 올바르지 않습니다.", 422) from exc
        analysis.edited_result = parsed.model_dump(mode="json")
        analysis.is_user_edited = True
        analysis.summary = parsed.summary
        analysis.updated_at = utc_now()
        await self.session.commit()
        await self.session.refresh(analysis)
        return self._public(analysis, current_input_hash=self._input_hash(input_text, extraction.id))

    async def delete_analysis(self, user_id: int, resume_id: int, file_id: int) -> ResumeAnalysisDeletedData:
        resume_file = await ResumeService(self.session).get_file(user_id, resume_id, file_id)
        analysis = await self.repository.get_analysis(user_id, resume_file.id)
        if not analysis:
            raise AppError("RESUME_ANALYSIS_NOT_FOUND", "이력서 분석 결과를 찾을 수 없습니다.", 404)
        await self.session.delete(analysis)
        await self.session.commit()
        return ResumeAnalysisDeletedData(deleted=True)

    async def list_runs(
        self, user_id: int, resume_id: int, file_id: int, page: int, size: int
    ) -> ResumeAnalysisRunsData:
        resume_file = await ResumeService(self.session).get_file(user_id, resume_id, file_id)
        runs, total = await self.repository.list_runs(user_id, resume_file.id, page, size)
        return ResumeAnalysisRunsData(
            items=[ResumeAnalysisRunPublic.model_validate(run) for run in runs],
            page=page,
            size=size,
            total=total,
            total_pages=ceil(total / size) if total else 0,
        )

    async def get_run(self, user_id: int, resume_id: int, file_id: int, run_id: int) -> ResumeAnalysisRunPublic:
        resume_file = await ResumeService(self.session).get_file(user_id, resume_id, file_id)
        run = await self.repository.get_run(user_id, resume_file.id, run_id)
        if not run:
            raise AppError("RESUME_ANALYSIS_RUN_NOT_FOUND", "이력서 분석 실행 이력을 찾을 수 없습니다.", 404)
        return ResumeAnalysisRunPublic.model_validate(run)

    async def get_profile_candidates(
        self, user_id: int, resume_id: int, file_id: int
    ) -> ResumeProfileCandidateData:
        analysis = await self.get_analysis(user_id, resume_id, file_id)
        return ResumeProfileCandidateData(
            items=[ResumeProfileCandidate.model_validate(item) for item in analysis.profile_candidates]
        )

    async def _get_ready_extraction(self, user_id: int, resume_file: ResumeFile) -> ResumeFileExtraction:
        extraction = await self.resume_repository.get_extraction(user_id, resume_file.id)
        if not extraction:
            raise AppError("RESUME_ANALYSIS_EXTRACTION_REQUIRED", "이력서 텍스트 추출이 먼저 필요합니다.", 409)
        if extraction.extraction_status == ResumeExtractionStatus.PROCESSING:
            raise AppError("RESUME_ANALYSIS_EXTRACTION_NOT_READY", "이력서 텍스트 추출이 아직 진행 중입니다.", 409)
        if extraction.extraction_status == ResumeExtractionStatus.OCR_REQUIRED:
            raise AppError("RESUME_ANALYSIS_EXTRACTION_NOT_READY", "OCR이 필요한 파일은 분석할 수 없습니다.", 409)
        if extraction.extraction_status != ResumeExtractionStatus.COMPLETED:
            raise AppError("RESUME_ANALYSIS_EXTRACTION_NOT_READY", "완료된 텍스트 추출 결과만 분석할 수 있습니다.", 409)
        return extraction

    def _analysis_input(self, extraction: ResumeFileExtraction) -> tuple[str, str]:
        if extraction.edited_text and extraction.edited_text.strip():
            text = extraction.edited_text.strip()
            source = "EDITED"
        else:
            text = (extraction.raw_text or "").strip()
            source = "RAW"
        if len(text) < RESUME_ANALYSIS_MIN_TEXT_LENGTH:
            raise AppError("RESUME_ANALYSIS_TEXT_EMPTY", "분석할 이력서 텍스트가 비어 있습니다.", 422)
        return text, source

    def _input_hash(self, text: str, extraction_id: int) -> str:
        return hashlib.sha256(f"{extraction_id}:{text}".encode()).hexdigest()

    async def _mark_failed(self, analysis: ResumeAnalysis, run: ResumeAnalysisRun, exc: Exception) -> None:
        now = utc_now()
        code = exc.code if isinstance(exc, AppError) else "RESUME_ANALYSIS_INVALID_OUTPUT"
        message = exc.message if isinstance(exc, AppError) else "이력서 분석에 실패했습니다."
        status = self._status_for_error(code)
        analysis.status = status
        analysis.error_code = code
        analysis.error_message = message[:500]
        analysis.updated_at = now
        run.status = status
        run.error_code = code
        run.error_message = message[:500]
        run.completed_at = now
        await self.session.commit()

    def _status_for_error(self, code: str) -> ResumeAnalysisStatus:
        if code in {
            "RESUME_ANALYSIS_PROVIDER_DISABLED",
            "RESUME_ANALYSIS_PROVIDER_UNAVAILABLE",
            "RESUME_ANALYSIS_PROVIDER_TIMEOUT",
        }:
            return ResumeAnalysisStatus.PROVIDER_UNAVAILABLE
        if code in {"RESUME_ANALYSIS_INVALID_OUTPUT", "RESUME_ANALYSIS_EVIDENCE_INVALID"}:
            return ResumeAnalysisStatus.INVALID_OUTPUT
        return ResumeAnalysisStatus.FAILED

    def _normalize_error(self, exc: Exception) -> AppError:
        if not isinstance(exc, AppError):
            return AppError("RESUME_ANALYSIS_INVALID_OUTPUT", "이력서 분석 결과 구조가 올바르지 않습니다.", 502)
        mapping = {
            "AI_PROVIDER_DISABLED": ("RESUME_ANALYSIS_PROVIDER_DISABLED", "이력서 AI Provider가 비활성화되어 있습니다.", 503),
            "AI_PROVIDER_UNAVAILABLE": ("RESUME_ANALYSIS_PROVIDER_UNAVAILABLE", "이력서 AI Provider가 응답하지 않습니다.", 502),
            "AI_PROVIDER_REQUEST_FAILED": ("RESUME_ANALYSIS_PROVIDER_UNAVAILABLE", "이력서 AI Provider 요청에 실패했습니다.", 502),
            "AI_PROVIDER_TIMEOUT": ("RESUME_ANALYSIS_PROVIDER_TIMEOUT", "이력서 AI 분석 요청 시간이 초과되었습니다.", 504),
            "AI_PROVIDER_INVALID_RESPONSE": ("RESUME_ANALYSIS_INVALID_OUTPUT", "이력서 AI 응답 구조가 올바르지 않습니다.", 502),
        }
        if exc.code not in mapping:
            return exc
        code, message, status_code = mapping[exc.code]
        return AppError(code, message, status_code)

    def _validate_evidence(self, parsed: ResumeAnalysisStructuredData, input_text: str, extraction_id: int) -> None:
        for collection_name in [
            "skills",
            "experiences",
            "projects",
            "education",
            "certifications",
            "achievements",
            "awards",
        ]:
            for item in getattr(parsed, collection_name):
                if not item.evidence:
                    raise AppError("RESUME_ANALYSIS_EVIDENCE_INVALID", f"{collection_name} 항목에 근거가 없습니다.", 502)
                for evidence in item.evidence:
                    if evidence.extraction_id is not None and evidence.extraction_id != extraction_id:
                        raise AppError("RESUME_ANALYSIS_EVIDENCE_INVALID", "Evidence extraction_id가 일치하지 않습니다.", 502)
                    if evidence.source_text not in input_text:
                        raise AppError("RESUME_ANALYSIS_EVIDENCE_INVALID", "Evidence 원문이 입력 텍스트에 없습니다.", 502)

    async def _build_profile_candidates(
        self, user_id: int, parsed: ResumeAnalysisStructuredData
    ) -> list[dict[str, Any]]:
        user_skills = await self.profile_repository.list_user_skills(user_id)
        existing_skill_names = {
            user_skill.skill.name.strip().lower()
            for user_skill in user_skills
            if user_skill.skill and user_skill.skill.name
        }
        candidates: list[dict[str, Any]] = []
        for skill in parsed.skills:
            action = "DUPLICATE" if skill.name.strip().lower() in existing_skill_names else "ADD"
            candidates.append(
                ResumeProfileCandidate(
                    target="skill",
                    action=action,
                    current_value=skill.name if action == "DUPLICATE" else None,
                    resume_value=skill.model_dump(mode="json"),
                    difference=None if action == "DUPLICATE" else "프로필에 없는 기술 후보입니다.",
                    evidence=[item.model_dump(mode="json") for item in skill.evidence],
                    confidence=skill.confidence,
                ).model_dump(mode="json")
            )
        for project in parsed.projects:
            candidates.append(
                ResumeProfileCandidate(
                    target="project",
                    action="ADD",
                    resume_value=project.model_dump(mode="json"),
                    difference="이력서에서 발견한 프로젝트 후보입니다.",
                    evidence=[item.model_dump(mode="json") for item in project.evidence],
                    confidence=project.confidence,
                ).model_dump(mode="json")
            )
        return candidates

    def _public(self, analysis: ResumeAnalysis, *, current_input_hash: str) -> ResumeAnalysisPublic:
        analysis.is_outdated = analysis.input_hash != current_input_hash
        return ResumeAnalysisPublic.model_validate(analysis)
