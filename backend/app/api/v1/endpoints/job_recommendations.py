from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_session
from app.models.job_recommendation import JobRecommendationFeedbackType, JobRecommendationGrade
from app.models.job_recommendation_automation import RecommendationChangeType
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.job_recommendation import (
    JobRecommendationDeletedData,
    JobRecommendationFeedbackCreate,
    JobRecommendationFeedbackPublic,
    JobRecommendationGenerateData,
    JobRecommendationGenerateRequest,
    JobRecommendationListData,
    JobRecommendationPolicyData,
    JobRecommendationPublic,
    JobRecommendationRunPublic,
    JobRecommendationRunsData,
)
from app.services.job_recommendation import JobRecommendationService
from app.services.job_recommendation_snapshot import JobRecommendationSnapshotService

router = APIRouter(prefix="/recommendations/jobs", tags=["job-recommendations"])


@router.post("/generate", response_model=ApiResponse[JobRecommendationGenerateData])
async def generate_job_recommendations(
    payload: JobRecommendationGenerateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobRecommendationGenerateData]:
    data = await JobRecommendationService(session).generate(current_user.id, payload)
    await JobRecommendationSnapshotService(session).create_for_run(current_user.id, data.run_id)
    return ApiResponse(success=True, data=data, message="규칙 기반 채용공고 추천이 생성되었습니다.")


@router.get("", response_model=ApiResponse[JobRecommendationListData])
async def list_job_recommendations(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    min_score: int | None = Query(default=None, ge=0, le=100),
    grade: JobRecommendationGrade | None = None,
    has_blocking_mismatch: bool | None = None,
    keyword: str | None = None,
    feedback: JobRecommendationFeedbackType | None = None,
    change_type: RecommendationChangeType | None = None,
    include_hidden: bool = False,
    include_outdated: bool = False,
    sort: str = Query(default="score", pattern="^(score|generated_at|job_deadline|company_name)$"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
) -> ApiResponse[JobRecommendationListData]:
    data = await JobRecommendationService(session).list_recommendations(
        current_user.id,
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
    return ApiResponse(success=True, data=data, message="규칙 기반 채용공고 추천 목록입니다.")


@router.get("/runs", response_model=ApiResponse[JobRecommendationRunsData])
async def list_job_recommendation_runs(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[JobRecommendationRunsData]:
    data = await JobRecommendationService(session).list_runs(current_user.id, page, size)
    return ApiResponse(success=True, data=data, message="추천 생성 실행 이력입니다.")


@router.get("/runs/{run_id}", response_model=ApiResponse[JobRecommendationRunPublic])
async def get_job_recommendation_run(
    run_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobRecommendationRunPublic]:
    data = await JobRecommendationService(session).get_run(current_user.id, run_id)
    return ApiResponse(success=True, data=data, message="추천 생성 실행 이력 상세입니다.")


@router.get("/policy", response_model=ApiResponse[JobRecommendationPolicyData])
async def get_job_recommendation_policy(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobRecommendationPolicyData]:
    _ = current_user
    data = JobRecommendationService(session).policy_data()
    return ApiResponse(success=True, data=data, message="규칙 기반 추천 정책입니다.")


@router.get("/{recommendation_id}", response_model=ApiResponse[JobRecommendationPublic])
async def get_job_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobRecommendationPublic]:
    data = await JobRecommendationService(session).get_recommendation(current_user.id, recommendation_id)
    return ApiResponse(success=True, data=data, message="규칙 기반 채용공고 추천 상세입니다.")


@router.post("/{recommendation_id}/refresh", response_model=ApiResponse[JobRecommendationPublic])
async def refresh_job_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobRecommendationPublic]:
    data = await JobRecommendationService(session).refresh(current_user.id, recommendation_id)
    return ApiResponse(success=True, data=data, message="추천 결과가 새로 계산되었습니다.")


@router.post(
    "/{recommendation_id}/feedback",
    response_model=ApiResponse[JobRecommendationFeedbackPublic],
    status_code=status.HTTP_201_CREATED,
)
async def create_job_recommendation_feedback(
    recommendation_id: int,
    payload: JobRecommendationFeedbackCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobRecommendationFeedbackPublic]:
    data = await JobRecommendationService(session).create_feedback(current_user.id, recommendation_id, payload)
    return ApiResponse(success=True, data=data, message="추천 피드백이 저장되었습니다.")


@router.delete("/{recommendation_id}/feedback", response_model=ApiResponse[JobRecommendationDeletedData])
async def delete_job_recommendation_feedback(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[JobRecommendationDeletedData]:
    data = await JobRecommendationService(session).delete_feedback(current_user.id, recommendation_id)
    return ApiResponse(success=True, data=data, message="추천 피드백이 삭제되었습니다.")
