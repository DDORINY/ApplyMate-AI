from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_session
from app.models.job import JobMatchStatus
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.job_match import (
    JobMatchDeletedData,
    JobMatchFeedbackCreate,
    JobMatchFeedbackListData,
    JobMatchFeedbackPublic,
    JobMatchFeedbackUpdate,
    JobMatchPublic,
    JobMatchRunRequest,
    JobMatchRunsData,
)
from app.services.job_match import JobMatchService

router = APIRouter(prefix="/jobs/{job_id}/match", tags=["job-match"])


@router.post("", response_model=ApiResponse[JobMatchPublic])
async def analyze_job_match(
    job_id: int,
    payload: JobMatchRunRequest | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobMatchPublic]:
    data = await JobMatchService(session).analyze_match(
        current_user.id,
        job_id,
        force=payload.force if payload else False,
        generate_explanation=payload.generate_explanation if payload else True,
    )
    return ApiResponse(success=True, data=data, message="공고 적합도 분석이 완료되었습니다.")


@router.get("", response_model=ApiResponse[JobMatchPublic])
async def get_job_match(
    job_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobMatchPublic]:
    data = await JobMatchService(session).get_match(current_user.id, job_id)
    return ApiResponse(success=True, data=data, message="공고 적합도 분석 결과입니다.")


@router.delete("", response_model=ApiResponse[JobMatchDeletedData])
async def delete_job_match(
    job_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobMatchDeletedData]:
    data = await JobMatchService(session).delete_match(current_user.id, job_id)
    return ApiResponse(success=True, data=data, message="공고 적합도 분석 결과가 삭제되었습니다.")


@router.get("/runs", response_model=ApiResponse[JobMatchRunsData])
async def list_job_match_runs(
    job_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    run_status: JobMatchStatus | None = Query(default=None, alias="status"),
) -> ApiResponse[JobMatchRunsData]:
    data = await JobMatchService(session).list_runs(
        current_user.id, job_id, page, size, run_status
    )
    return ApiResponse(success=True, data=data, message="공고 적합도 분석 실행 이력입니다.")


@router.post(
    "/feedback",
    response_model=ApiResponse[JobMatchFeedbackPublic],
    status_code=status.HTTP_201_CREATED,
)
async def create_job_match_feedback(
    job_id: int,
    payload: JobMatchFeedbackCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobMatchFeedbackPublic]:
    data = await JobMatchService(session).create_feedback(current_user.id, job_id, payload)
    return ApiResponse(success=True, data=data, message="적합도 분석 피드백이 저장되었습니다.")


@router.get("/feedback", response_model=ApiResponse[JobMatchFeedbackListData])
async def list_job_match_feedback(
    job_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobMatchFeedbackListData]:
    data = await JobMatchService(session).list_feedback(current_user.id, job_id)
    return ApiResponse(success=True, data=data, message="적합도 분석 피드백 목록입니다.")


@router.patch("/feedback/{feedback_id}", response_model=ApiResponse[JobMatchFeedbackPublic])
async def update_job_match_feedback(
    job_id: int,
    feedback_id: int,
    payload: JobMatchFeedbackUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobMatchFeedbackPublic]:
    data = await JobMatchService(session).update_feedback(
        current_user.id, job_id, feedback_id, payload
    )
    return ApiResponse(success=True, data=data, message="적합도 분석 피드백이 수정되었습니다.")


@router.delete("/feedback/{feedback_id}", response_model=ApiResponse[dict[str, bool]])
async def delete_job_match_feedback(
    job_id: int,
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, bool]]:
    data = await JobMatchService(session).delete_feedback(current_user.id, job_id, feedback_id)
    return ApiResponse(success=True, data=data, message="적합도 분석 피드백이 삭제되었습니다.")
