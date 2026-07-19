from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.job_analysis import (
    JobAnalysisDeletedData,
    JobAnalysisPublic,
    JobAnalysisRunRequest,
    JobAnalysisRunsData,
    JobAnalysisUpdate,
)
from app.services.job_analysis import JobAnalysisService

router = APIRouter(prefix="/jobs/{job_id}/analysis", tags=["job-analysis"])


@router.post("", response_model=ApiResponse[JobAnalysisPublic])
async def analyze_job(
    job_id: int,
    payload: JobAnalysisRunRequest | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobAnalysisPublic]:
    data = await JobAnalysisService(session).analyze_job(
        current_user.id, job_id, force=payload.force if payload else False
    )
    return ApiResponse(success=True, data=data, message="채용공고 분석이 완료되었습니다.")


@router.get("", response_model=ApiResponse[JobAnalysisPublic])
async def get_job_analysis(
    job_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobAnalysisPublic]:
    data = await JobAnalysisService(session).get_analysis(current_user.id, job_id)
    return ApiResponse(success=True, data=data, message="채용공고 분석 결과입니다.")


@router.patch("", response_model=ApiResponse[JobAnalysisPublic])
async def update_job_analysis(
    job_id: int,
    payload: JobAnalysisUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobAnalysisPublic]:
    data = await JobAnalysisService(session).update_analysis(current_user.id, job_id, payload)
    return ApiResponse(success=True, data=data, message="채용공고 분석 결과가 수정되었습니다.")


@router.delete("", response_model=ApiResponse[JobAnalysisDeletedData])
async def delete_job_analysis(
    job_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobAnalysisDeletedData]:
    data = await JobAnalysisService(session).delete_analysis(current_user.id, job_id)
    return ApiResponse(success=True, data=data, message="채용공고 분석 결과가 삭제되었습니다.")


@router.get("/runs", response_model=ApiResponse[JobAnalysisRunsData])
async def list_job_analysis_runs(
    job_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[JobAnalysisRunsData]:
    data = await JobAnalysisService(session).list_runs(current_user.id, job_id, page, size)
    return ApiResponse(success=True, data=data, message="채용공고 분석 실행 이력입니다.")
