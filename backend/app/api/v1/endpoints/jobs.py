from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_session
from app.models.job import (
    JobDeadlineType,
    JobEmploymentType,
    JobPostingStatus,
    JobSourceType,
    JobWorkType,
)
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.job import (
    JobPostingCreate,
    JobPostingDeletedData,
    JobPostingImportData,
    JobPostingListData,
    JobPostingPublic,
    JobPostingUpdate,
    JobPostingUrlImportRequest,
)
from app.services.job import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=ApiResponse[JobPostingPublic], status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobPostingCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobPostingPublic]:
    job = await JobService(session).create_job(current_user.id, payload)
    return ApiResponse(
        success=True,
        data=JobPostingPublic.model_validate(job),
        message="채용공고가 등록되었습니다.",
    )


@router.post(
    "/import-url",
    response_model=ApiResponse[JobPostingImportData],
    status_code=status.HTTP_201_CREATED,
)
async def import_job_url(
    payload: JobPostingUrlImportRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobPostingImportData]:
    data = await JobService(session).import_url(current_user.id, payload)
    return ApiResponse(success=True, data=data, message="URL 기반 채용공고가 등록되었습니다.")


@router.get("", response_model=ApiResponse[JobPostingListData])
async def list_jobs(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    query: str | None = None,
    status_filter: JobPostingStatus | None = Query(default=None, alias="status"),
    employment_type: JobEmploymentType | None = None,
    work_type: JobWorkType | None = None,
    company_id: int | None = None,
    deadline_from: datetime | None = None,
    deadline_to: datetime | None = None,
    deadline_type: JobDeadlineType | None = None,
    is_favorite: bool | None = None,
    source_type: JobSourceType | None = None,
    sort: str = Query(default="created_at", pattern="^(created_at|updated_at|deadline_at|title)$"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
) -> ApiResponse[JobPostingListData]:
    data = await JobService(session).list_jobs(
        current_user.id,
        page=page,
        size=size,
        query_text=query,
        status=status_filter,
        employment_type=employment_type,
        work_type=work_type,
        company_id=company_id,
        deadline_from=deadline_from,
        deadline_to=deadline_to,
        deadline_type=deadline_type,
        is_favorite=is_favorite,
        source_type=source_type,
        sort=sort,
        order=order,
    )
    return ApiResponse(success=True, data=data, message="채용공고 목록입니다.")


@router.get("/{job_id}", response_model=ApiResponse[JobPostingPublic])
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobPostingPublic]:
    job = await JobService(session).get_job(current_user.id, job_id)
    return ApiResponse(
        success=True,
        data=JobPostingPublic.model_validate(job),
        message="채용공고 상세입니다.",
    )


@router.patch("/{job_id}", response_model=ApiResponse[JobPostingPublic])
async def update_job(
    job_id: int,
    payload: JobPostingUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobPostingPublic]:
    job = await JobService(session).update_job(current_user.id, job_id, payload)
    return ApiResponse(
        success=True,
        data=JobPostingPublic.model_validate(job),
        message="채용공고가 수정되었습니다.",
    )


@router.delete("/{job_id}", response_model=ApiResponse[JobPostingDeletedData])
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobPostingDeletedData]:
    await JobService(session).delete_job(current_user.id, job_id)
    return ApiResponse(
        success=True,
        data=JobPostingDeletedData(deleted=True),
        message="채용공고가 삭제되었습니다.",
    )
