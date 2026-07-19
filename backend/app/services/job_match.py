from math import ceil

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.security import utc_now
from app.models.job import (
    JobAnalysis,
    JobAnalysisStatus,
    JobMatch,
    JobMatchFeedback,
    JobMatchRun,
    JobMatchStatus,
    JobPosting,
)
from app.repositories.job import JobRepository
from app.repositories.job_analysis import JobAnalysisRepository
from app.repositories.job_match import JobMatchRepository
from app.repositories.profile import ProfileRepository
from app.schemas.job_match import (
    JobMatchDeletedData,
    JobMatchFeedbackCreate,
    JobMatchFeedbackListData,
    JobMatchFeedbackPublic,
    JobMatchFeedbackUpdate,
    JobMatchPublic,
    JobMatchRunsData,
    JobMatchRunPublic,
    JobMatchScores,
)
from app.services.job_analysis import analysis_input_hash
from app.services.job_match_scoring import (
    CALCULATION_VERSION,
    JobMatchScoringEngine,
    MatchCalculation,
    ProfileSnapshot,
    job_analysis_hash,
    profile_hash,
)


class JobMatchService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.job_repository = JobRepository(session)
        self.analysis_repository = JobAnalysisRepository(session)
        self.profile_repository = ProfileRepository(session)
        self.repository = JobMatchRepository(session)
        self.scoring_engine = JobMatchScoringEngine()

    async def analyze_match(
        self,
        user_id: int,
        job_id: int,
        *,
        force: bool = False,
        generate_explanation: bool = True,
    ) -> JobMatchPublic:
        job, analysis, snapshot = await self._load_inputs(user_id, job_id)
        current_profile_hash = profile_hash(snapshot)
        current_analysis_hash = job_analysis_hash(analysis)
        existing = await self.repository.get_match(user_id, job_id)

        if (
            existing
            and existing.status == JobMatchStatus.COMPLETED
            and existing.profile_hash == current_profile_hash
            and existing.job_analysis_hash == current_analysis_hash
            and existing.calculation_version == CALCULATION_VERSION
            and not force
        ):
            return self._public(
                existing,
                current_profile_hash=current_profile_hash,
                current_job_analysis_hash=current_analysis_hash,
            )
        if existing and existing.status == JobMatchStatus.PROCESSING:
            raise AppError("JOB_MATCH_ALREADY_RUNNING", "적합도 분석이 이미 진행 중입니다.", 409)

        now = utc_now()
        run = JobMatchRun(
            user_id=user_id,
            job_posting_id=job_id,
            job_analysis_id=analysis.id,
            status=JobMatchStatus.PROCESSING,
            profile_hash=current_profile_hash,
            job_analysis_hash=current_analysis_hash,
            calculation_version=CALCULATION_VERSION,
            started_at=now,
        )
        self.session.add(run)
        if existing:
            existing.status = JobMatchStatus.PROCESSING
            existing.updated_at = now
        await self.session.commit()
        await self.session.refresh(run)

        try:
            calculation = self.scoring_engine.calculate(snapshot, job, analysis)
            explanation_provider = self._explanation_provider(generate_explanation)
            match = existing or JobMatch(
                user_id=user_id,
                job_posting_id=job_id,
                job_analysis_id=analysis.id,
                profile_hash=current_profile_hash,
                job_analysis_hash=current_analysis_hash,
                calculation_version=CALCULATION_VERSION,
                explanation_provider=explanation_provider,
            )
            self._apply_calculation(
                match,
                calculation,
                analysis=analysis,
                profile_hash_value=current_profile_hash,
                job_analysis_hash_value=current_analysis_hash,
                explanation_provider=explanation_provider,
            )
            self.session.add(match)
            await self.session.flush()

            run.job_match_id = match.id
            run.status = JobMatchStatus.COMPLETED
            run.total_score = calculation.total_score
            run.result_snapshot = calculation.snapshot()
            run.completed_at = utc_now()
            await self.session.commit()
            await self.session.refresh(match)
            return self._public(
                match,
                current_profile_hash=current_profile_hash,
                current_job_analysis_hash=current_analysis_hash,
            )
        except Exception as exc:
            await self._mark_failed(run.id, existing, exc)
            if isinstance(exc, AppError):
                raise
            raise AppError("JOB_MATCH_FAILED", "적합도 분석에 실패했습니다.", 500) from exc

    async def get_match(self, user_id: int, job_id: int) -> JobMatchPublic:
        _job, analysis, snapshot = await self._load_inputs(user_id, job_id, require_fresh=False)
        match = await self.repository.get_match(user_id, job_id)
        if not match:
            raise AppError("JOB_MATCH_NOT_FOUND", "저장된 적합도 분석 결과가 없습니다.", 404)
        return self._public(
            match,
            current_profile_hash=profile_hash(snapshot),
            current_job_analysis_hash=job_analysis_hash(analysis),
        )

    async def delete_match(self, user_id: int, job_id: int) -> JobMatchDeletedData:
        await self._get_job(user_id, job_id)
        match = await self.repository.get_match(user_id, job_id)
        if not match:
            raise AppError("JOB_MATCH_NOT_FOUND", "저장된 적합도 분석 결과가 없습니다.", 404)
        await self.session.delete(match)
        await self.session.commit()
        return JobMatchDeletedData(deleted=True)

    async def list_runs(
        self,
        user_id: int,
        job_id: int,
        page: int,
        size: int,
        status: JobMatchStatus | None = None,
    ) -> JobMatchRunsData:
        await self._get_job(user_id, job_id)
        runs, total = await self.repository.list_runs(user_id, job_id, page, size, status)
        return JobMatchRunsData(
            items=[JobMatchRunPublic.model_validate(run) for run in runs],
            page=page,
            size=size,
            total=total,
            total_pages=ceil(total / size) if total else 0,
        )

    async def create_feedback(
        self, user_id: int, job_id: int, payload: JobMatchFeedbackCreate
    ) -> JobMatchFeedbackPublic:
        match = await self._get_match_for_feedback(user_id, job_id)
        feedback = JobMatchFeedback(
            user_id=user_id,
            job_match_id=match.id,
            feedback_type=payload.feedback_type,
            rating=payload.rating,
            comment=payload.comment,
        )
        self.session.add(feedback)
        await self.session.commit()
        await self.session.refresh(feedback)
        return JobMatchFeedbackPublic.model_validate(feedback)

    async def list_feedback(self, user_id: int, job_id: int) -> JobMatchFeedbackListData:
        match = await self._get_match_for_feedback(user_id, job_id)
        items = await self.repository.list_feedback(user_id, match.id)
        return JobMatchFeedbackListData(
            items=[JobMatchFeedbackPublic.model_validate(item) for item in items]
        )

    async def update_feedback(
        self, user_id: int, job_id: int, feedback_id: int, payload: JobMatchFeedbackUpdate
    ) -> JobMatchFeedbackPublic:
        await self._get_match_for_feedback(user_id, job_id)
        feedback = await self.repository.get_feedback(user_id, feedback_id)
        if not feedback:
            raise AppError("JOB_MATCH_FEEDBACK_NOT_FOUND", "피드백을 찾을 수 없습니다.", 404)
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(feedback, key, value)
        feedback.updated_at = utc_now()
        await self.session.commit()
        await self.session.refresh(feedback)
        return JobMatchFeedbackPublic.model_validate(feedback)

    async def delete_feedback(self, user_id: int, job_id: int, feedback_id: int) -> dict[str, bool]:
        await self._get_match_for_feedback(user_id, job_id)
        feedback = await self.repository.get_feedback(user_id, feedback_id)
        if not feedback:
            raise AppError("JOB_MATCH_FEEDBACK_NOT_FOUND", "피드백을 찾을 수 없습니다.", 404)
        await self.session.delete(feedback)
        await self.session.commit()
        return {"deleted": True}

    async def _load_inputs(
        self, user_id: int, job_id: int, *, require_fresh: bool = True
    ) -> tuple[JobPosting, JobAnalysis, ProfileSnapshot]:
        job = await self._get_job(user_id, job_id)
        analysis = await self.analysis_repository.get_analysis(user_id, job_id)
        if not analysis or analysis.status != JobAnalysisStatus.COMPLETED:
            raise AppError("JOB_ANALYSIS_REQUIRED", "완료된 채용공고 분석이 먼저 필요합니다.", 409)
        if require_fresh and analysis.input_hash != analysis_input_hash(job):
            raise AppError("JOB_ANALYSIS_OUTDATED", "채용공고가 변경되어 공고 재분석이 필요합니다.", 409)

        profile = await self.profile_repository.get_profile(user_id)
        if not profile:
            raise AppError("JOB_MATCH_PROFILE_REQUIRED", "커리어 프로필을 먼저 작성해야 합니다.", 409)
        skills = await self.profile_repository.list_user_skills(user_id)
        preferences = await self.profile_repository.get_preferences(user_id)
        if not skills or not preferences:
            raise AppError(
                "JOB_MATCH_PROFILE_INCOMPLETE",
                "적합도 분석에는 사용자 기술과 희망 조건이 필요합니다.",
                409,
            )
        snapshot = ProfileSnapshot(
            profile=profile,
            skills=skills,
            experiences=await self.profile_repository.list_experiences(user_id),
            projects=await self.profile_repository.list_projects(user_id),
            preferences=preferences,
            exclusions=await self.profile_repository.list_exclusions(user_id),
        )
        return job, analysis, snapshot

    async def _get_job(self, user_id: int, job_id: int) -> JobPosting:
        job = await self.job_repository.get_job(user_id, job_id)
        if not job:
            raise AppError("JOB_POSTING_NOT_FOUND", "채용공고를 찾을 수 없습니다.", 404)
        return job

    async def _get_match_for_feedback(self, user_id: int, job_id: int) -> JobMatch:
        await self._get_job(user_id, job_id)
        match = await self.repository.get_match(user_id, job_id)
        if not match:
            raise AppError("JOB_MATCH_NOT_FOUND", "저장된 적합도 분석 결과가 없습니다.", 404)
        return match

    async def _mark_failed(
        self, run_id: int, existing: JobMatch | None, exc: Exception
    ) -> None:
        now = utc_now()
        run = await self.session.get(JobMatchRun, run_id)
        code = exc.code if isinstance(exc, AppError) else exc.__class__.__name__
        message = exc.message if isinstance(exc, AppError) else "적합도 분석에 실패했습니다."
        if run:
            run.status = JobMatchStatus.FAILED
            run.error_code = code
            run.error_message = message[:500]
            run.completed_at = now
        if existing:
            existing.status = JobMatchStatus.FAILED
            existing.updated_at = now
        await self.session.commit()

    def _apply_calculation(
        self,
        match: JobMatch,
        calculation: MatchCalculation,
        *,
        analysis: JobAnalysis,
        profile_hash_value: str,
        job_analysis_hash_value: str,
        explanation_provider: str,
    ) -> None:
        now = utc_now()
        match.job_analysis_id = analysis.id
        match.status = JobMatchStatus.COMPLETED
        match.total_score = calculation.total_score
        match.grade = calculation.grade
        match.recommendation_status = calculation.recommendation_status
        match.role_score = calculation.role_score
        match.skill_score = calculation.skill_score
        match.experience_score = calculation.experience_score
        match.project_score = calculation.project_score
        match.preference_score = calculation.preference_score
        match.risk_score = calculation.risk_score
        match.matched_skills = calculation.matched_skills
        match.missing_skills = calculation.missing_skills
        match.matched_projects = calculation.matched_projects
        match.strengths = calculation.strengths
        match.gaps = calculation.gaps
        match.risks = calculation.risks
        match.recommendation_summary = calculation.recommendation_summary
        match.profile_completeness = calculation.profile_completeness
        match.profile_hash = profile_hash_value
        match.job_analysis_hash = job_analysis_hash_value
        match.calculation_version = CALCULATION_VERSION
        match.explanation_provider = explanation_provider
        match.calculated_at = now
        match.updated_at = now

    def _public(
        self,
        match: JobMatch,
        *,
        current_profile_hash: str,
        current_job_analysis_hash: str,
    ) -> JobMatchPublic:
        return JobMatchPublic(
            id=match.id,
            user_id=match.user_id,
            job_posting_id=match.job_posting_id,
            job_analysis_id=match.job_analysis_id,
            status=match.status,
            total_score=match.total_score,
            grade=match.grade,
            recommendation_status=match.recommendation_status,
            scores=JobMatchScores(
                role=match.role_score,
                skill=match.skill_score,
                experience=match.experience_score,
                project=match.project_score,
                preference=match.preference_score,
                risk=match.risk_score,
            ),
            matched_skills=match.matched_skills or [],
            missing_skills=match.missing_skills or [],
            matched_projects=match.matched_projects or [],
            strengths=match.strengths or [],
            gaps=match.gaps or [],
            risks=match.risks or [],
            recommendation_summary=match.recommendation_summary,
            profile_completeness=match.profile_completeness,
            profile_hash=match.profile_hash,
            job_analysis_hash=match.job_analysis_hash,
            calculation_version=match.calculation_version,
            explanation_provider=match.explanation_provider,
            is_outdated=(
                match.profile_hash != current_profile_hash
                or match.job_analysis_hash != current_job_analysis_hash
            ),
            calculated_at=match.calculated_at,
            created_at=match.created_at,
            updated_at=match.updated_at,
        )

    def _explanation_provider(self, generate_explanation: bool) -> str:
        if not generate_explanation:
            return "template"
        provider = get_settings().ai_provider
        return provider if provider != "disabled" else "template"
