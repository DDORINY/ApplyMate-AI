import hashlib
from math import ceil
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.security import utc_now
from app.models.job import Company, JobPosting, JobSourceType
from app.repositories.job import JobRepository
from app.schemas.job import (
    JobPostingCreate,
    JobPostingImportData,
    JobPostingListData,
    JobPostingPublic,
    JobPostingUpdate,
    JobPostingUrlImportRequest,
)
from app.services.job_url_importer import fetch_url_content


def normalize_company_name(name: str) -> str:
    return " ".join(name.strip().lower().split())


def content_hash_for(
    company_name: str, title: str, source_url: str | None, description: str | None
) -> str:
    source = "|".join(
        [
            normalize_company_name(company_name),
            " ".join(title.lower().split()),
            (source_url or "").strip().lower(),
            (description or "").strip().lower()[:4000],
        ]
    )
    return hashlib.sha256(source.encode()).hexdigest()


def validate_job_constraints(job: JobPosting) -> None:
    if (
        job.salary_min is not None
        and job.salary_max is not None
        and job.salary_min > job.salary_max
    ):
        raise AppError(
            "JOB_INVALID_SALARY_RANGE", "최대 급여는 최소 급여보다 작을 수 없습니다.", 422
        )
    if (
        job.published_at is not None
        and job.deadline_at is not None
        and job.published_at > job.deadline_at
    ):
        raise AppError("JOB_INVALID_DEADLINE", "마감일은 게시일보다 빠를 수 없습니다.", 422)
    if job.deadline_type.value == "FIXED" and job.deadline_at is None:
        raise AppError("JOB_DEADLINE_REQUIRED", "고정 마감 공고는 마감일이 필요합니다.", 422)


class JobService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = JobRepository(session)

    async def get_or_create_company(
        self,
        name: str,
        website_url: str | None,
        company_size,
        industry: str | None,
        description: str | None,
    ) -> Company:
        normalized_name = normalize_company_name(name)
        company = await self.repository.get_company_by_normalized_name(normalized_name)
        if company:
            if website_url and not company.website_url:
                company.website_url = website_url
            if company_size and company.company_size.value == "UNKNOWN":
                company.company_size = company_size
            if industry and not company.industry:
                company.industry = industry
            if description and not company.description:
                company.description = description
            return company
        company = Company(
            name=name.strip(),
            normalized_name=normalized_name,
            website_url=website_url,
            company_size=company_size,
            industry=industry,
            description=description,
        )
        self.session.add(company)
        await self.session.flush()
        await self.session.refresh(company)
        return company

    async def create_job(self, user_id: int, payload: JobPostingCreate) -> JobPosting:
        company = await self.get_or_create_company(
            payload.company_name,
            payload.company_website_url,
            payload.company_size,
            payload.company_industry,
            payload.company_description,
        )
        content_hash = content_hash_for(
            company.name, payload.title, payload.source_url, payload.description
        )
        await self.ensure_not_duplicate(
            user_id,
            company.id,
            payload.title,
            payload.deadline_at,
            payload.source_url,
            content_hash,
        )
        data = payload.model_dump(
            exclude={
                "company_name",
                "company_website_url",
                "company_size",
                "company_industry",
                "company_description",
            }
        )
        source_url = data.get("source_url")
        job = JobPosting(
            user_id=user_id,
            company_id=company.id,
            content_hash=content_hash,
            source_site=urlparse(source_url).netloc.lower() if source_url else None,
            **data,
        )
        validate_job_constraints(job)
        self.session.add(job)
        await self.session.commit()
        return await self.get_job(user_id, job.id)

    async def import_url(
        self, user_id: int, payload: JobPostingUrlImportRequest
    ) -> JobPostingImportData:
        imported = fetch_url_content(payload.url)
        title = payload.title or imported.title or "제목 미확인 채용공고"
        company_name = payload.company_name or imported.source_site or "기업명 미확인"
        description = payload.description or imported.description or imported.text
        warnings = list(imported.warnings)
        if not payload.company_name:
            warnings.append("기업명은 URL 또는 사용자 입력으로 보완이 필요할 수 있습니다.")
        if not payload.title and not imported.title:
            warnings.append("공고 제목을 자동 추출하지 못해 기본 제목으로 저장했습니다.")
        create_payload = JobPostingCreate(
            company_name=company_name,
            title=title,
            description=description,
            source_type=JobSourceType.URL,
            source_url=imported.final_url,
            original_content=imported.text,
            status=payload.status,
            is_favorite=payload.is_favorite,
            notes=payload.notes,
            collected_at=utc_now(),
        )
        job = await self.create_job(user_id, create_payload)
        return JobPostingImportData(
            job=JobPostingPublic.model_validate(job),
            import_status="SUCCESS" if not warnings else "PARTIAL",
            extracted_fields=imported.extracted_fields,
            warnings=warnings,
        )

    async def ensure_not_duplicate(
        self,
        user_id: int,
        company_id: int,
        title: str,
        deadline_at,
        source_url: str | None,
        content_hash: str,
        exclude_job_id: int | None = None,
    ) -> None:
        duplicate = None
        if source_url:
            duplicate = await self.repository.get_duplicate_by_source_url(
                user_id, source_url, exclude_job_id
            )
        duplicate = duplicate or await self.repository.get_duplicate_by_company_title_deadline(
            user_id, company_id, title, deadline_at, exclude_job_id
        )
        duplicate = duplicate or await self.repository.get_duplicate_by_content_hash(
            user_id, content_hash, exclude_job_id
        )
        if duplicate:
            raise AppError(
                "JOB_POSTING_ALREADY_EXISTS",
                f"이미 등록된 채용공고입니다. job_id={duplicate.id}",
                409,
            )

    async def list_jobs(self, user_id: int, **filters) -> JobPostingListData:
        page = filters.pop("page")
        size = filters.pop("size")
        jobs, total = await self.repository.list_jobs(user_id, page=page, size=size, **filters)
        return JobPostingListData(
            items=[JobPostingPublic.model_validate(job) for job in jobs],
            page=page,
            size=size,
            total=total,
            total_pages=ceil(total / size) if total else 0,
        )

    async def get_job(self, user_id: int, job_id: int) -> JobPosting:
        job = await self.repository.get_job(user_id, job_id)
        if not job:
            raise AppError("JOB_POSTING_NOT_FOUND", "채용공고를 찾을 수 없습니다.", 404)
        return job

    async def update_job(self, user_id: int, job_id: int, payload: JobPostingUpdate) -> JobPosting:
        job = await self.get_job(user_id, job_id)
        data = payload.model_dump(exclude_unset=True)
        company_fields = {
            "company_name",
            "company_website_url",
            "company_size",
            "company_industry",
            "company_description",
        }
        if company_fields.intersection(data):
            company = await self.get_or_create_company(
                data.pop("company_name", job.company.name),
                data.pop("company_website_url", job.company.website_url),
                data.pop("company_size", job.company.company_size),
                data.pop("company_industry", job.company.industry),
                data.pop("company_description", job.company.description),
            )
            job.company_id = company.id
            job.company = company
        for key, value in data.items():
            setattr(job, key, value)
        job.content_hash = content_hash_for(
            job.company.name, job.title, job.source_url, job.description
        )
        validate_job_constraints(job)
        await self.ensure_not_duplicate(
            user_id,
            job.company_id,
            job.title,
            job.deadline_at,
            job.source_url,
            job.content_hash,
            exclude_job_id=job.id,
        )
        await self.session.commit()
        return await self.get_job(user_id, job_id)

    async def delete_job(self, user_id: int, job_id: int) -> None:
        job = await self.get_job(user_id, job_id)
        await self.session.delete(job)
        await self.session.commit()
