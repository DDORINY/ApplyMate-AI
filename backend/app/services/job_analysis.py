import hashlib
import re
from datetime import timedelta
from math import ceil

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.job_analysis_prompt import SYSTEM_PROMPT, build_user_prompt
from app.ai.providers import get_ai_provider, provider_status
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.security import utc_now
from app.models.job import JobAnalysis, JobAnalysisRun, JobAnalysisStatus, JobPosting
from app.repositories.job import JobRepository
from app.repositories.job_analysis import JobAnalysisRepository
from app.schemas.job_analysis import (
    AIProviderStatusData,
    JobAnalysisDeletedData,
    JobAnalysisPublic,
    JobAnalysisRunsData,
    JobAnalysisRunPublic,
    JobAnalysisStructuredData,
    JobAnalysisUpdate,
)

TAG_RE = re.compile(r"<[^>]+>")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


class JobAnalysisService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.job_repository = JobRepository(session)
        self.repository = JobAnalysisRepository(session)

    def get_provider_status(self) -> AIProviderStatusData:
        return AIProviderStatusData.model_validate(provider_status(get_settings()))

    async def analyze_job(
        self, user_id: int, job_id: int, *, force: bool = False
    ) -> JobAnalysisPublic:
        settings = get_settings()
        job = await self._get_job(user_id, job_id)
        analysis_input = build_analysis_input(job, settings.ai_analysis_max_input_chars)
        input_hash = analysis_input_hash(job)
        existing = await self.repository.get_analysis(user_id, job_id)
        if (
            existing
            and existing.status == JobAnalysisStatus.COMPLETED
            and existing.input_hash == input_hash
            and not force
        ):
            return self._public(existing, current_input_hash=input_hash)
        if existing and existing.status == JobAnalysisStatus.PROCESSING:
            raise AppError("JOB_ANALYSIS_ALREADY_RUNNING", "이미 분석이 진행 중입니다.", 409)
        await self._enforce_limits(user_id, force=force)

        provider = get_ai_provider(settings)
        started_at = utc_now()
        run = JobAnalysisRun(
            user_id=user_id,
            job_posting_id=job_id,
            status=JobAnalysisStatus.PROCESSING,
            provider=provider.provider,
            model=provider.model,
            schema_version=settings.ai_analysis_schema_version,
            prompt_version=settings.ai_analysis_prompt_version,
            input_hash=input_hash,
            input_length=len(analysis_input),
            started_at=started_at,
        )
        self.session.add(run)
        if existing:
            existing.status = JobAnalysisStatus.PROCESSING
            existing.updated_at = started_at
        await self.session.commit()
        await self.session.refresh(run)

        try:
            result = await provider.analyze_job(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=build_user_prompt(analysis_input, settings),
                response_schema=JobAnalysisStructuredData,
            )
            parsed = JobAnalysisStructuredData.model_validate(result.parsed_data)
            now = utc_now()
            analysis = existing or JobAnalysis(
                user_id=user_id,
                job_posting_id=job_id,
                schema_version=settings.ai_analysis_schema_version,
                prompt_version=settings.ai_analysis_prompt_version,
                input_hash=input_hash,
                input_length=len(analysis_input),
            )
            self._apply_structured_data(analysis, parsed, input_hash, len(analysis_input), now)
            self.session.add(analysis)
            await self.session.flush()
            run.job_analysis_id = analysis.id
            run.status = JobAnalysisStatus.COMPLETED
            run.request_id = result.request_id
            run.prompt_tokens = result.prompt_tokens
            run.completion_tokens = result.completion_tokens
            run.total_tokens = result.total_tokens
            run.latency_ms = result.latency_ms
            run.raw_response = result.raw_response if settings.ai_store_raw_response else None
            run.completed_at = now
            await self.session.commit()
            await self.session.refresh(analysis)
            return self._public(analysis, current_input_hash=input_hash)
        except (AppError, ValidationError, ValueError) as exc:
            await self._mark_failed(run.id, existing, exc)
            if isinstance(exc, AppError):
                raise
            raise AppError("AI_PROVIDER_INVALID_RESPONSE", "AI 분석 결과 구조가 올바르지 않습니다.", 502) from exc

    async def get_analysis(self, user_id: int, job_id: int) -> JobAnalysisPublic:
        job = await self._get_job(user_id, job_id)
        analysis = await self.repository.get_analysis(user_id, job_id)
        if not analysis:
            raise AppError("JOB_ANALYSIS_NOT_FOUND", "채용공고 분석 결과를 찾을 수 없습니다.", 404)
        return self._public(analysis, current_input_hash=analysis_input_hash(job))

    async def update_analysis(
        self, user_id: int, job_id: int, payload: JobAnalysisUpdate
    ) -> JobAnalysisPublic:
        job = await self._get_job(user_id, job_id)
        analysis = await self.repository.get_analysis(user_id, job_id)
        if not analysis:
            raise AppError("JOB_ANALYSIS_NOT_FOUND", "채용공고 분석 결과를 찾을 수 없습니다.", 404)
        data = payload.model_dump(exclude_unset=True)
        if not data:
            return self._public(analysis, current_input_hash=analysis_input_hash(job))
        for key, value in data.items():
            setattr(analysis, key, value)
        analysis.is_user_edited = True
        analysis.status = JobAnalysisStatus.COMPLETED
        analysis.updated_at = utc_now()
        await self.session.commit()
        await self.session.refresh(analysis)
        return self._public(analysis, current_input_hash=analysis_input_hash(job))

    async def delete_analysis(self, user_id: int, job_id: int) -> JobAnalysisDeletedData:
        await self._get_job(user_id, job_id)
        analysis = await self.repository.get_analysis(user_id, job_id)
        if not analysis:
            raise AppError("JOB_ANALYSIS_NOT_FOUND", "채용공고 분석 결과를 찾을 수 없습니다.", 404)
        await self.session.delete(analysis)
        await self.session.commit()
        return JobAnalysisDeletedData(deleted=True)

    async def list_runs(self, user_id: int, job_id: int, page: int, size: int) -> JobAnalysisRunsData:
        await self._get_job(user_id, job_id)
        runs, total = await self.repository.list_runs(user_id, job_id, page, size)
        return JobAnalysisRunsData(
            items=[JobAnalysisRunPublic.model_validate(run) for run in runs],
            page=page,
            size=size,
            total=total,
            total_pages=ceil(total / size) if total else 0,
        )

    async def _get_job(self, user_id: int, job_id: int) -> JobPosting:
        job = await self.job_repository.get_job(user_id, job_id)
        if not job:
            raise AppError("JOB_POSTING_NOT_FOUND", "채용공고를 찾을 수 없습니다.", 404)
        return job

    async def _enforce_limits(self, user_id: int, *, force: bool) -> None:
        settings = get_settings()
        since = utc_now() - timedelta(days=1)
        if await self.repository.count_runs_since(user_id, since) >= settings.ai_daily_analysis_limit:
            raise AppError("AI_DAILY_ANALYSIS_LIMIT_EXCEEDED", "일일 AI 분석 한도를 초과했습니다.", 429)
        if force:
            return
        latest = await self.repository.latest_run(user_id)
        if latest and (utc_now() - latest.created_at).total_seconds() < settings.ai_analysis_cooldown_seconds:
            raise AppError("AI_ANALYSIS_COOLDOWN", "잠시 후 다시 분석을 요청해 주세요.", 429)

    async def _mark_failed(
        self, run_id: int, existing: JobAnalysis | None, exc: Exception
    ) -> None:
        now = utc_now()
        run = await self.session.get(JobAnalysisRun, run_id)
        code = exc.code if isinstance(exc, AppError) else exc.__class__.__name__
        message = exc.message if isinstance(exc, AppError) else "AI 분석에 실패했습니다."
        if run:
            run.status = JobAnalysisStatus.FAILED
            run.error_code = code
            run.error_message = message[:500]
            run.completed_at = now
        if existing:
            existing.status = JobAnalysisStatus.FAILED
            existing.updated_at = now
        await self.session.commit()

    def _apply_structured_data(
        self, analysis: JobAnalysis, parsed: JobAnalysisStructuredData, input_hash: str, input_length: int, now
    ) -> None:
        analysis.status = JobAnalysisStatus.COMPLETED
        analysis.schema_version = get_settings().ai_analysis_schema_version
        analysis.prompt_version = get_settings().ai_analysis_prompt_version
        analysis.input_hash = input_hash
        analysis.input_length = input_length
        analysis.summary = parsed.summary
        analysis.position_data = parsed.position.model_dump(mode="json")
        analysis.responsibilities = [item.model_dump(mode="json") for item in parsed.responsibilities]
        analysis.required_qualifications = [
            item.model_dump(mode="json") for item in parsed.required_qualifications
        ]
        analysis.preferred_qualifications = [
            item.model_dump(mode="json") for item in parsed.preferred_qualifications
        ]
        analysis.technical_skills = [item.model_dump(mode="json") for item in parsed.technical_skills]
        analysis.experience_data = parsed.experience.model_dump(mode="json")
        analysis.education_data = parsed.education.model_dump(mode="json")
        analysis.work_conditions = parsed.work_conditions.model_dump(mode="json")
        analysis.recruitment_process = parsed.recruitment_process
        analysis.deadline_data = parsed.deadline.model_dump(mode="json")
        analysis.company_values = [item.model_dump(mode="json") for item in parsed.company_values]
        analysis.keywords = parsed.keywords
        analysis.warnings = [item.model_dump(mode="json") for item in parsed.warnings]
        analysis.confidence = parsed.confidence.model_dump(mode="json")
        analysis.is_user_edited = False
        analysis.analyzed_at = now
        analysis.updated_at = now

    def _public(self, analysis: JobAnalysis, *, current_input_hash: str) -> JobAnalysisPublic:
        return JobAnalysisPublic(
            id=analysis.id,
            job_posting_id=analysis.job_posting_id,
            user_id=analysis.user_id,
            status=analysis.status,
            schema_version=analysis.schema_version,
            prompt_version=analysis.prompt_version,
            input_hash=analysis.input_hash,
            input_length=analysis.input_length,
            summary=analysis.summary,
            position_data=analysis.position_data,
            responsibilities=analysis.responsibilities,
            required_qualifications=analysis.required_qualifications,
            preferred_qualifications=analysis.preferred_qualifications,
            technical_skills=analysis.technical_skills,
            experience_data=analysis.experience_data,
            education_data=analysis.education_data,
            work_conditions=analysis.work_conditions,
            recruitment_process=analysis.recruitment_process,
            deadline_data=analysis.deadline_data,
            company_values=analysis.company_values,
            keywords=analysis.keywords,
            warnings=analysis.warnings,
            confidence=analysis.confidence,
            is_user_edited=analysis.is_user_edited,
            is_outdated=analysis.input_hash != current_input_hash,
            analyzed_at=analysis.analyzed_at,
            created_at=analysis.created_at,
            updated_at=analysis.updated_at,
        )


def build_analysis_input(job: JobPosting, max_chars: int) -> str:
    values = [
        ("기업명", job.company.name if job.company else ""),
        ("공고 제목", job.title),
        ("직무", job.position),
        ("고용 형태", job.employment_type.value if job.employment_type else None),
        ("경력 조건", job.career_requirement),
        ("학력 조건", job.education_requirement),
        ("근무 지역", job.location),
        ("근무 형태", job.work_type.value if job.work_type else None),
        ("급여", _salary_text(job)),
        ("주요 업무", job.description),
        ("필수 조건", job.requirements),
        ("우대 조건", job.preferred_qualifications),
        ("복지", job.benefits),
        ("채용 절차", job.recruitment_process),
        ("마감일", job.deadline_at.isoformat() if job.deadline_at else None),
        ("마감 유형", job.deadline_type.value if job.deadline_type else None),
        ("원문 URL", job.source_url),
        ("원문 내용", job.original_content),
    ]
    lines: list[str] = []
    seen: set[str] = set()
    for label, value in values:
        cleaned = _clean_text(value)
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"{label}: {cleaned}")
    text = "\n".join(lines).strip()
    if not text:
        raise AppError("JOB_ANALYSIS_INPUT_EMPTY", "분석할 채용공고 내용이 없습니다.", 422)
    return text[:max_chars]


def analysis_input_hash(job: JobPosting) -> str:
    text = build_analysis_input(job, 1_000_000)
    return hashlib.sha256(text.encode()).hexdigest()


def _clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = TAG_RE.sub(" ", text)
    text = CONTROL_RE.sub(" ", text)
    return "\n".join(" ".join(line.split()) for line in text.splitlines() if line.strip())


def _salary_text(job: JobPosting) -> str:
    parts = []
    if job.salary_min is not None:
        parts.append(f"min={job.salary_min}")
    if job.salary_max is not None:
        parts.append(f"max={job.salary_max}")
    if job.salary_text:
        parts.append(job.salary_text)
    return " ".join(parts)
