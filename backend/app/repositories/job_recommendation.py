from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application
from app.models.career import CareerProfile, Experience, JobPreference, Project, ProjectSkill, UserSkill
from app.models.job import Company, JobAnalysis, JobPosting, JobPostingStatus
from app.models.job_recommendation import (
    JobRecommendation,
    JobRecommendationFeedback,
    JobRecommendationFeedbackType,
    JobRecommendationGrade,
    JobRecommendationRun,
    JobRecommendationStatus,
)


class JobRecommendationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_profile_bundle(self, user_id: int) -> tuple[CareerProfile | None, list[UserSkill], list[Experience], list[Project], JobPreference | None]:
        profile = await self.session.scalar(select(CareerProfile).where(CareerProfile.user_id == user_id))
        skills_result = await self.session.execute(
            select(UserSkill)
            .options(selectinload(UserSkill.skill))
            .where(UserSkill.user_id == user_id)
            .order_by(UserSkill.is_primary.desc(), UserSkill.id)
        )
        experiences_result = await self.session.execute(
            select(Experience).where(Experience.user_id == user_id).order_by(Experience.start_date.desc())
        )
        projects_result = await self.session.execute(
            select(Project)
            .options(selectinload(Project.project_skills).selectinload(ProjectSkill.skill))
            .where(Project.user_id == user_id)
            .order_by(Project.start_date.desc(), Project.id.desc())
        )
        preferences = await self.session.scalar(select(JobPreference).where(JobPreference.user_id == user_id))
        return (
            profile,
            list(skills_result.scalars().all()),
            list(experiences_result.scalars().all()),
            list(projects_result.scalars().all()),
            preferences,
        )

    async def list_candidate_jobs(
        self,
        user_id: int,
        *,
        include_without_analysis: bool,
        exclude_applied_jobs: bool,
        force_include_job_id: int | None = None,
        limit: int = 200,
    ) -> tuple[list[JobPosting], int]:
        query = (
            select(JobPosting)
            .options(
                selectinload(JobPosting.company),
                selectinload(JobPosting.analysis),
                selectinload(JobPosting.match),
            )
            .where(JobPosting.user_id == user_id)
            .where(JobPosting.status.in_([JobPostingStatus.SAVED, JobPostingStatus.REVIEWING, JobPostingStatus.INTERESTED]))
        )
        query = query.where(or_(JobPosting.deadline_at.is_(None), JobPosting.deadline_at > func.now()))
        if not include_without_analysis:
            query = query.join(JobAnalysis, JobAnalysis.job_posting_id == JobPosting.id)
        if exclude_applied_jobs:
            applied = select(Application.job_id).where(Application.user_id == user_id, Application.job_id.is_not(None))
            query = query.where(JobPosting.id.not_in(applied))
        if force_include_job_id:
            query = query.where(JobPosting.id == force_include_job_id)
        total_result = await self.session.execute(select(func.count()).select_from(query.order_by(None).subquery()))
        total = int(total_result.scalar_one())
        result = await self.session.execute(query.order_by(JobPosting.updated_at.desc(), JobPosting.id.desc()).limit(limit))
        return list(result.scalars().all()), total

    async def feedback_excluded_job_ids(self, user_id: int) -> set[int]:
        result = await self.session.execute(
            select(JobRecommendation.job_id)
            .join(JobRecommendationFeedback, JobRecommendationFeedback.recommendation_id == JobRecommendation.id)
            .where(
                JobRecommendation.user_id == user_id,
                JobRecommendationFeedback.user_id == user_id,
                JobRecommendationFeedback.feedback_type.in_(
                    [JobRecommendationFeedbackType.HIDDEN, JobRecommendationFeedbackType.NOT_INTERESTED]
                ),
            )
        )
        return {int(row[0]) for row in result.all()}

    async def get_existing_by_snapshot(
        self,
        user_id: int,
        job_id: int,
        profile_hash: str,
        job_hash: str,
        policy_version: str,
    ) -> JobRecommendation | None:
        result = await self.session.execute(
            select(JobRecommendation)
            .options(
                selectinload(JobRecommendation.reasons),
                selectinload(JobRecommendation.feedback),
                selectinload(JobRecommendation.job).selectinload(JobPosting.company),
                selectinload(JobRecommendation.job).selectinload(JobPosting.analysis),
                selectinload(JobRecommendation.job).selectinload(JobPosting.match),
            )
            .where(
                JobRecommendation.user_id == user_id,
                JobRecommendation.job_id == job_id,
                JobRecommendation.profile_hash == profile_hash,
                JobRecommendation.job_hash == job_hash,
                JobRecommendation.policy_version == policy_version,
            )
        )
        return result.scalar_one_or_none()

    async def get_recommendation(self, user_id: int, recommendation_id: int) -> JobRecommendation | None:
        result = await self.session.execute(
            select(JobRecommendation)
            .options(
                selectinload(JobRecommendation.reasons),
                selectinload(JobRecommendation.feedback),
                selectinload(JobRecommendation.run),
                selectinload(JobRecommendation.job).selectinload(JobPosting.company),
                selectinload(JobRecommendation.job).selectinload(JobPosting.analysis),
                selectinload(JobRecommendation.job).selectinload(JobPosting.match),
            )
            .where(JobRecommendation.id == recommendation_id, JobRecommendation.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_recommendations(
        self,
        user_id: int,
        *,
        page: int,
        size: int,
        min_score: int | None = None,
        grade: JobRecommendationGrade | None = None,
        has_blocking_mismatch: bool | None = None,
        keyword: str | None = None,
        feedback: JobRecommendationFeedbackType | None = None,
        include_hidden: bool = False,
        include_outdated: bool = False,
        sort: str = "score",
        order: str = "desc",
    ) -> tuple[list[JobRecommendation], int]:
        query = (
            select(JobRecommendation)
            .join(JobRecommendation.job)
            .join(JobPosting.company)
            .options(
                selectinload(JobRecommendation.reasons),
                selectinload(JobRecommendation.feedback),
                selectinload(JobRecommendation.job).selectinload(JobPosting.company),
                selectinload(JobRecommendation.job).selectinload(JobPosting.analysis),
                selectinload(JobRecommendation.job).selectinload(JobPosting.match),
            )
            .where(JobRecommendation.user_id == user_id)
        )
        if min_score is not None:
            query = query.where(JobRecommendation.score >= min_score)
        if grade:
            query = query.where(JobRecommendation.grade == grade)
        if has_blocking_mismatch is not None:
            query = query.where(JobRecommendation.has_blocking_mismatch == has_blocking_mismatch)
        if not include_hidden:
            query = query.where(JobRecommendation.status != JobRecommendationStatus.HIDDEN)
        if not include_outdated:
            query = query.where(JobRecommendation.outdated.is_(False))
        if keyword:
            pattern = f"%{keyword.lower()}%"
            query = query.where(
                or_(
                    func.lower(JobPosting.title).like(pattern),
                    func.lower(JobPosting.position).like(pattern),
                    func.lower(Company.name).like(pattern),
                )
            )
        if feedback:
            query = query.join(JobRecommendationFeedback).where(
                and_(
                    JobRecommendationFeedback.user_id == user_id,
                    JobRecommendationFeedback.feedback_type == feedback,
                )
            )
        total_result = await self.session.execute(select(func.count()).select_from(query.order_by(None).subquery()))
        total = int(total_result.scalar_one())
        sort_column = {
            "score": JobRecommendation.score,
            "generated_at": JobRecommendation.generated_at,
            "job_deadline": JobPosting.deadline_at,
            "company_name": Company.name,
        }.get(sort, JobRecommendation.score)
        order_clause = sort_column.asc() if order == "asc" else sort_column.desc()
        result = await self.session.execute(
            query.order_by(order_clause, JobRecommendation.id.desc()).offset((page - 1) * size).limit(size)
        )
        return list(result.scalars().unique().all()), total

    async def list_runs(self, user_id: int, page: int, size: int) -> tuple[list[JobRecommendationRun], int]:
        base = select(JobRecommendationRun).where(JobRecommendationRun.user_id == user_id)
        total_result = await self.session.execute(select(func.count()).select_from(base.order_by(None).subquery()))
        total = int(total_result.scalar_one())
        result = await self.session.execute(
            base.order_by(JobRecommendationRun.created_at.desc(), JobRecommendationRun.id.desc()).offset((page - 1) * size).limit(size)
        )
        return list(result.scalars().all()), total

    async def get_run(self, user_id: int, run_id: int) -> JobRecommendationRun | None:
        result = await self.session.execute(
            select(JobRecommendationRun).where(JobRecommendationRun.id == run_id, JobRecommendationRun.user_id == user_id)
        )
        return result.scalar_one_or_none()
