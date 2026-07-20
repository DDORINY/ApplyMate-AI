from math import ceil

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.security import utc_now
from app.models.job_recommendation import (
    JobRecommendation,
    JobRecommendationFeedback,
    JobRecommendationFeedbackType,
    JobRecommendationGrade,
    JobRecommendationReason,
    JobRecommendationRun,
    JobRecommendationRunStatus,
    JobRecommendationStatus,
    JobRecommendationType,
)
from app.models.job_recommendation_automation import RecommendationChangeType
from app.repositories.job_recommendation import JobRecommendationRepository
from app.repositories.job_recommendation_automation import JobRecommendationAutomationRepository
from app.schemas.job_recommendation import (
    JobRecommendationDeletedData,
    JobRecommendationFeedbackCreate,
    JobRecommendationFeedbackPublic,
    JobRecommendationGenerateData,
    JobRecommendationGenerateRequest,
    JobRecommendationJobSummary,
    JobRecommendationListData,
    JobRecommendationPolicyData,
    JobRecommendationPublic,
    JobRecommendationReasonPublic,
    JobRecommendationRunPublic,
    JobRecommendationRunsData,
)
from app.services.job_recommendation_policy import (
    POLICY_VERSION,
    SCORE_WEIGHTS,
    JobRecommendationPolicy,
    RecommendationProfile,
    profile_hash,
    recommendation_job_hash,
)


class JobRecommendationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = JobRecommendationRepository(session)
        self.automation_repository = JobRecommendationAutomationRepository(session)
        self.policy = JobRecommendationPolicy()

    async def generate(self, user_id: int, payload: JobRecommendationGenerateRequest) -> JobRecommendationGenerateData:
        now = utc_now()
        run = JobRecommendationRun(
            user_id=user_id,
            status=JobRecommendationRunStatus.PROCESSING,
            policy_version=POLICY_VERSION,
            started_at=now,
        )
        self.session.add(run)
        await self.session.flush()

        profile = await self._profile(user_id)
        jobs, candidate_total = await self.repository.list_candidate_jobs(
            user_id,
            include_without_analysis=payload.include_jobs_without_analysis,
            exclude_applied_jobs=payload.exclude_applied_jobs,
            limit=payload.max_jobs,
        )
        excluded_job_ids = await self.repository.feedback_excluded_job_ids(user_id)
        recommended_count = 0
        excluded_count = max(0, candidate_total - len(jobs))
        failed_count = 0

        for job in jobs:
            if job.id in excluded_job_ids:
                excluded_count += 1
                continue
            try:
                calculation = self.policy.calculate(profile, job, job.analysis, job.match)
                current_profile_hash = profile_hash(profile)
                current_job_hash = recommendation_job_hash(job, job.analysis, job.match)
                existing = await self.repository.get_existing_by_snapshot(
                    user_id, job.id, current_profile_hash, current_job_hash, POLICY_VERSION
                )
                if existing and not payload.force_refresh:
                    existing.run_id = run.id
                    existing.status = JobRecommendationStatus.ACTIVE
                    existing.outdated = False
                    existing.generated_at = now
                    recommended_count += 1
                    continue
                recommendation = existing or JobRecommendation(
                    user_id=user_id,
                    job_id=job.id,
                    profile_hash=current_profile_hash,
                    job_hash=current_job_hash,
                    policy_version=POLICY_VERSION,
                )
                self.apply_calculation(recommendation, run.id, calculation, job.analysis, job.match)
                self.session.add(recommendation)
                await self.session.flush()
                if existing:
                    for reason in list(existing.reasons):
                        await self.session.delete(reason)
                    await self.session.flush()
                for reason in calculation.reasons:
                    self.session.add(
                        JobRecommendationReason(
                            recommendation_id=recommendation.id,
                            reason_type=reason.reason_type,
                            requirement_type=reason.requirement_type,
                            label=reason.label,
                            normalized_value=reason.normalized_value,
                            match_status=reason.match_status,
                            weight=reason.weight,
                            score_delta=reason.score_delta,
                            severity=reason.severity,
                            evidence=reason.evidence,
                        )
                    )
                recommended_count += 1
            except Exception:
                failed_count += 1

        run.status = JobRecommendationRunStatus.COMPLETED
        run.input_job_count = len(jobs)
        run.recommended_count = recommended_count
        run.excluded_count = excluded_count
        run.failed_count = failed_count
        run.completed_at = utc_now()
        await self.session.commit()
        return JobRecommendationGenerateData(
            run_id=run.id,
            status=run.status,
            policy_version=run.policy_version,
            input_job_count=run.input_job_count,
            recommended_count=run.recommended_count,
            excluded_count=run.excluded_count,
            failed_count=run.failed_count,
        )

    async def refresh(self, user_id: int, recommendation_id: int) -> JobRecommendationPublic:
        recommendation = await self._get_recommendation(user_id, recommendation_id)
        payload = JobRecommendationGenerateRequest(force_refresh=True, include_jobs_without_analysis=True, exclude_applied_jobs=False, max_jobs=1)
        now = utc_now()
        run = JobRecommendationRun(user_id=user_id, status=JobRecommendationRunStatus.PROCESSING, policy_version=POLICY_VERSION, started_at=now)
        self.session.add(run)
        await self.session.flush()
        profile = await self._profile(user_id)
        jobs, _total = await self.repository.list_candidate_jobs(
            user_id,
            include_without_analysis=True,
            exclude_applied_jobs=False,
            force_include_job_id=recommendation.job_id,
            limit=payload.max_jobs,
        )
        if not jobs:
            raise AppError("JOB_RECOMMENDATION_JOB_NOT_FOUND", "추천을 새로 계산할 공고를 찾을 수 없습니다.", 404)
        job = jobs[0]
        calculation = self.policy.calculate(profile, job, job.analysis, job.match)
        self.apply_calculation(recommendation, run.id, calculation, job.analysis, job.match)
        for reason in list(recommendation.reasons):
            await self.session.delete(reason)
        await self.session.flush()
        for reason in calculation.reasons:
            self.session.add(
                JobRecommendationReason(
                    recommendation_id=recommendation.id,
                    reason_type=reason.reason_type,
                    requirement_type=reason.requirement_type,
                    label=reason.label,
                    normalized_value=reason.normalized_value,
                    match_status=reason.match_status,
                    weight=reason.weight,
                    score_delta=reason.score_delta,
                    severity=reason.severity,
                    evidence=reason.evidence,
                )
            )
        run.status = JobRecommendationRunStatus.COMPLETED
        run.input_job_count = 1
        run.recommended_count = 1
        run.completed_at = utc_now()
        await self.session.commit()
        refreshed = await self._get_recommendation(user_id, recommendation.id)
        return await self.public(refreshed)

    def apply_calculation(self, recommendation: JobRecommendation, run_id: int, calculation, analysis, match) -> None:
        now = utc_now()
        recommendation.run_id = run_id
        recommendation.score = calculation.score
        recommendation.grade = calculation.grade
        recommendation.recommendation_type = JobRecommendationType.RULE_BASED
        recommendation.has_blocking_mismatch = calculation.has_blocking_mismatch
        recommendation.matched_count = calculation.matched_count
        recommendation.missing_count = calculation.missing_count
        recommendation.unknown_count = calculation.unknown_count
        recommendation.profile_hash = calculation.input_snapshot["profile_hash"]
        recommendation.job_hash = calculation.input_snapshot["job_hash"]
        recommendation.job_analysis_id = analysis.id if analysis else None
        recommendation.matching_analysis_id = match.id if match else None
        recommendation.policy_version = POLICY_VERSION
        recommendation.input_snapshot = calculation.input_snapshot
        recommendation.score_breakdown = calculation.score_breakdown
        recommendation.missing_profile_fields = calculation.missing_profile_fields
        recommendation.outdated = False
        recommendation.status = JobRecommendationStatus.ACTIVE
        recommendation.generated_at = now
        recommendation.updated_at = now

    async def list_recommendations(
        self,
        user_id: int,
        *,
        page: int,
        size: int,
        min_score: int | None,
        grade: JobRecommendationGrade | None,
        has_blocking_mismatch: bool | None,
        keyword: str | None,
        feedback: JobRecommendationFeedbackType | None,
        change_type: RecommendationChangeType | None,
        include_hidden: bool,
        include_outdated: bool,
        sort: str,
        order: str,
    ) -> JobRecommendationListData:
        items, total = await self.repository.list_recommendations(
            user_id,
            page=page,
            size=size,
            min_score=min_score,
            grade=grade,
            has_blocking_mismatch=has_blocking_mismatch,
            keyword=keyword,
            feedback=feedback,
            change_type=change_type,
            include_hidden=include_hidden,
            include_outdated=include_outdated,
            sort=sort,
            order=order,
        )
        profile = await self._profile(user_id)
        public_items = [await self.public(item, profile=profile) for item in items]
        return JobRecommendationListData(
            items=public_items,
            page=page,
            size=size,
            total=total,
            total_pages=ceil(total / size) if total else 0,
        )

    async def get_recommendation(self, user_id: int, recommendation_id: int) -> JobRecommendationPublic:
        recommendation = await self._get_recommendation(user_id, recommendation_id)
        return await self.public(recommendation)

    async def create_feedback(
        self, user_id: int, recommendation_id: int, payload: JobRecommendationFeedbackCreate
    ) -> JobRecommendationFeedbackPublic:
        recommendation = await self._get_recommendation(user_id, recommendation_id)
        existing = next((item for item in recommendation.feedback if item.user_id == user_id), None)
        if existing:
            feedback = existing
            feedback.feedback_type = payload.feedback_type
            feedback.reason_code = payload.reason_code
            feedback.comment = payload.comment
            feedback.updated_at = utc_now()
        else:
            feedback = JobRecommendationFeedback(
                user_id=user_id,
                recommendation_id=recommendation.id,
                feedback_type=payload.feedback_type,
                reason_code=payload.reason_code,
                comment=payload.comment,
            )
            self.session.add(feedback)
        if payload.feedback_type == JobRecommendationFeedbackType.HIDDEN:
            recommendation.status = JobRecommendationStatus.HIDDEN
        elif recommendation.status == JobRecommendationStatus.HIDDEN:
            recommendation.status = JobRecommendationStatus.ACTIVE
        await self.session.commit()
        await self.session.refresh(feedback)
        return JobRecommendationFeedbackPublic.model_validate(feedback)

    async def delete_feedback(self, user_id: int, recommendation_id: int) -> JobRecommendationDeletedData:
        recommendation = await self._get_recommendation(user_id, recommendation_id)
        feedback = next((item for item in recommendation.feedback if item.user_id == user_id), None)
        if not feedback:
            raise AppError("JOB_RECOMMENDATION_FEEDBACK_NOT_FOUND", "추천 피드백을 찾을 수 없습니다.", 404)
        await self.session.delete(feedback)
        if recommendation.status == JobRecommendationStatus.HIDDEN:
            recommendation.status = JobRecommendationStatus.ACTIVE
        await self.session.commit()
        return JobRecommendationDeletedData(deleted=True)

    async def list_runs(self, user_id: int, page: int, size: int) -> JobRecommendationRunsData:
        runs, total = await self.repository.list_runs(user_id, page, size)
        return JobRecommendationRunsData(
            items=[JobRecommendationRunPublic.model_validate(run) for run in runs],
            page=page,
            size=size,
            total=total,
            total_pages=ceil(total / size) if total else 0,
        )

    async def get_run(self, user_id: int, run_id: int) -> JobRecommendationRunPublic:
        run = await self.repository.get_run(user_id, run_id)
        if not run:
            raise AppError("JOB_RECOMMENDATION_RUN_NOT_FOUND", "추천 실행 이력을 찾을 수 없습니다.", 404)
        return JobRecommendationRunPublic.model_validate(run)

    def policy_data(self) -> JobRecommendationPolicyData:
        return JobRecommendationPolicyData(
            recommendation_type="RULE_BASED",
            policy_version=POLICY_VERSION,
            weights=SCORE_WEIGHTS,
            grades={
                "EXCELLENT": "85~100",
                "GOOD": "70~84",
                "POSSIBLE": "50~69",
                "LOW": "0~49",
                "BLOCKED": "필수 조건 미충족",
            },
            note="규칙 기반 추천입니다. AI, 머신러닝, 외부 공고 수집을 사용하지 않습니다.",
        )

    async def _profile(self, user_id: int) -> RecommendationProfile:
        profile, skills, experiences, projects, preferences = await self.repository.get_profile_bundle(user_id)
        return RecommendationProfile(profile=profile, skills=skills, experiences=experiences, projects=projects, preferences=preferences)

    async def _get_recommendation(self, user_id: int, recommendation_id: int) -> JobRecommendation:
        recommendation = await self.repository.get_recommendation(user_id, recommendation_id)
        if not recommendation:
            raise AppError("JOB_RECOMMENDATION_NOT_FOUND", "추천 결과를 찾을 수 없습니다.", 404)
        return recommendation

    async def public(self, recommendation: JobRecommendation, profile: RecommendationProfile | None = None) -> JobRecommendationPublic:
        profile = profile or await self._profile(recommendation.user_id)
        current_profile_hash = profile_hash(profile)
        current_job_hash = recommendation_job_hash(recommendation.job, recommendation.job.analysis, recommendation.job.match)
        is_outdated = (
            recommendation.profile_hash != current_profile_hash
            or recommendation.job_hash != current_job_hash
            or recommendation.policy_version != POLICY_VERSION
        )
        if is_outdated and not recommendation.outdated:
            recommendation.outdated = True
            recommendation.status = JobRecommendationStatus.OUTDATED
            await self.session.commit()
        feedback = next((item for item in recommendation.feedback if item.user_id == recommendation.user_id), None)
        latest_item = await self.automation_repository.latest_item_for_recommendation(recommendation.user_id, recommendation.id)
        company_name = recommendation.job.company.name if recommendation.job.company else "회사명 미상"
        return JobRecommendationPublic(
            id=recommendation.id,
            user_id=recommendation.user_id,
            job_id=recommendation.job_id,
            run_id=recommendation.run_id,
            score=recommendation.score,
            grade=recommendation.grade,
            recommendation_type=recommendation.recommendation_type,
            has_blocking_mismatch=recommendation.has_blocking_mismatch,
            matched_count=recommendation.matched_count,
            missing_count=recommendation.missing_count,
            unknown_count=recommendation.unknown_count,
            policy_version=recommendation.policy_version,
            score_breakdown=recommendation.score_breakdown or {},
            input_snapshot=recommendation.input_snapshot or {},
            missing_profile_fields=recommendation.missing_profile_fields or [],
            outdated=is_outdated,
            status=recommendation.status,
            generated_at=recommendation.generated_at,
            created_at=recommendation.created_at,
            updated_at=recommendation.updated_at,
            job=JobRecommendationJobSummary(
                id=recommendation.job.id,
                title=recommendation.job.title,
                position=recommendation.job.position,
                company_name=company_name,
                employment_type=recommendation.job.employment_type.value,
                location=recommendation.job.location,
                deadline_at=recommendation.job.deadline_at,
                status=recommendation.job.status.value,
            ),
            reasons=[JobRecommendationReasonPublic.model_validate(reason) for reason in recommendation.reasons],
            feedback=JobRecommendationFeedbackPublic.model_validate(feedback) if feedback else None,
            latest_change_type=latest_item.change_type if latest_item else None,
            previous_score=latest_item.previous_score if latest_item else None,
            score_delta=latest_item.score_delta if latest_item else None,
            previous_grade=latest_item.previous_grade if latest_item else None,
            rank=latest_item.rank if latest_item else None,
            rank_delta=latest_item.rank_delta if latest_item else None,
            missing_job_fields=latest_item.missing_job_fields if latest_item and latest_item.missing_job_fields else [],
            data_completeness_score=latest_item.data_completeness_score if latest_item else None,
            recommendation_confidence=latest_item.recommendation_confidence if latest_item else None,
        )
