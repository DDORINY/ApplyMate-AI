from datetime import datetime

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.job import (
    Company,
    JobDeadlineType,
    JobEmploymentType,
    JobPosting,
    JobPostingStatus,
    JobSourceType,
    JobWorkType,
)


class JobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_company_by_normalized_name(self, normalized_name: str) -> Company | None:
        result = await self.session.execute(
            select(Company).where(Company.normalized_name == normalized_name)
        )
        return result.scalar_one_or_none()

    async def get_job(self, user_id: int, job_id: int) -> JobPosting | None:
        result = await self.session.execute(
            select(JobPosting)
            .options(selectinload(JobPosting.company))
            .where(JobPosting.id == job_id, JobPosting.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_duplicate_by_source_url(
        self, user_id: int, source_url: str, exclude_job_id: int | None = None
    ) -> JobPosting | None:
        query = select(JobPosting).where(
            JobPosting.user_id == user_id,
            JobPosting.source_url == source_url,
        )
        if exclude_job_id:
            query = query.where(JobPosting.id != exclude_job_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_duplicate_by_content_hash(
        self, user_id: int, content_hash: str, exclude_job_id: int | None = None
    ) -> JobPosting | None:
        query = select(JobPosting).where(
            JobPosting.user_id == user_id,
            JobPosting.content_hash == content_hash,
        )
        if exclude_job_id:
            query = query.where(JobPosting.id != exclude_job_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_duplicate_by_company_title_deadline(
        self,
        user_id: int,
        company_id: int,
        title: str,
        deadline_at: datetime | None,
        exclude_job_id: int | None = None,
    ) -> JobPosting | None:
        query = select(JobPosting).where(
            JobPosting.user_id == user_id,
            JobPosting.company_id == company_id,
            func.lower(JobPosting.title) == title.lower(),
        )
        if deadline_at is None:
            query = query.where(JobPosting.deadline_at.is_(None))
        else:
            query = query.where(JobPosting.deadline_at == deadline_at)
        if exclude_job_id:
            query = query.where(JobPosting.id != exclude_job_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_jobs(
        self,
        user_id: int,
        page: int,
        size: int,
        query_text: str | None = None,
        status: JobPostingStatus | None = None,
        employment_type: JobEmploymentType | None = None,
        work_type: JobWorkType | None = None,
        company_id: int | None = None,
        deadline_from: datetime | None = None,
        deadline_to: datetime | None = None,
        deadline_type: JobDeadlineType | None = None,
        is_favorite: bool | None = None,
        source_type: JobSourceType | None = None,
        sort: str = "created_at",
        order: str = "desc",
    ) -> tuple[list[JobPosting], int]:
        base = select(JobPosting).join(JobPosting.company).where(JobPosting.user_id == user_id)
        base = self.apply_filters(
            base,
            query_text=query_text,
            status=status,
            employment_type=employment_type,
            work_type=work_type,
            company_id=company_id,
            deadline_from=deadline_from,
            deadline_to=deadline_to,
            deadline_type=deadline_type,
            is_favorite=is_favorite,
            source_type=source_type,
        )
        total_result = await self.session.execute(
            select(func.count()).select_from(base.order_by(None).subquery())
        )
        total = int(total_result.scalar_one())

        sort_column = {
            "created_at": JobPosting.created_at,
            "updated_at": JobPosting.updated_at,
            "deadline_at": JobPosting.deadline_at,
            "title": JobPosting.title,
        }.get(sort, JobPosting.created_at)
        order_clause = sort_column.asc() if order == "asc" else sort_column.desc()
        result = await self.session.execute(
            base.options(selectinload(JobPosting.company))
            .order_by(order_clause, JobPosting.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().all()), total

    def apply_filters(
        self,
        query: Select[tuple[JobPosting]],
        *,
        query_text: str | None,
        status: JobPostingStatus | None,
        employment_type: JobEmploymentType | None,
        work_type: JobWorkType | None,
        company_id: int | None,
        deadline_from: datetime | None,
        deadline_to: datetime | None,
        deadline_type: JobDeadlineType | None,
        is_favorite: bool | None,
        source_type: JobSourceType | None,
    ) -> Select[tuple[JobPosting]]:
        if query_text:
            pattern = f"%{query_text.lower()}%"
            query = query.where(
                or_(
                    func.lower(JobPosting.title).like(pattern),
                    func.lower(JobPosting.position).like(pattern),
                    func.lower(Company.name).like(pattern),
                    func.lower(JobPosting.location).like(pattern),
                    func.lower(JobPosting.description).like(pattern),
                    func.lower(JobPosting.notes).like(pattern),
                )
            )
        if status:
            query = query.where(JobPosting.status == status)
        if employment_type:
            query = query.where(JobPosting.employment_type == employment_type)
        if work_type:
            query = query.where(JobPosting.work_type == work_type)
        if company_id:
            query = query.where(JobPosting.company_id == company_id)
        if deadline_from:
            query = query.where(JobPosting.deadline_at >= deadline_from)
        if deadline_to:
            query = query.where(JobPosting.deadline_at <= deadline_to)
        if deadline_type:
            query = query.where(JobPosting.deadline_type == deadline_type)
        if is_favorite is not None:
            query = query.where(JobPosting.is_favorite == is_favorite)
        if source_type:
            query = query.where(JobPosting.source_type == source_type)
        return query
