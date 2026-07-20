from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.document_improvement import (
    DocumentImprovementApplyData,
    DocumentImprovementApplyRequest,
    DocumentImprovementCreateRequest,
    DocumentImprovementDeletedData,
    DocumentImprovementListData,
    DocumentImprovementRejectData,
    DocumentImprovementRunPublic,
    DocumentImprovementSuggestionPublic,
    DocumentImprovementSuggestionUpdate,
)
from app.services.document_improvement import DocumentImprovementService

router = APIRouter(prefix="/documents", tags=["document-improvements"])


@router.post("/{document_id}/improvements", response_model=ApiResponse[DocumentImprovementRunPublic], status_code=status.HTTP_201_CREATED)
async def create_document_improvement(
    document_id: int,
    payload: DocumentImprovementCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[DocumentImprovementRunPublic]:
    run = await DocumentImprovementService(session).create_run(current_user.id, document_id, payload)
    return ApiResponse(success=True, data=run, message="지원 문서 개선안이 생성되었습니다.")


@router.get("/{document_id}/improvements", response_model=ApiResponse[DocumentImprovementListData])
async def list_document_improvements(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[DocumentImprovementListData]:
    data = await DocumentImprovementService(session).list_runs(current_user.id, document_id, page, size)
    return ApiResponse(success=True, data=data, message="지원 문서 개선 실행 목록입니다.")


@router.get("/{document_id}/improvements/{run_id}", response_model=ApiResponse[DocumentImprovementRunPublic])
async def get_document_improvement(
    document_id: int,
    run_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[DocumentImprovementRunPublic]:
    run = await DocumentImprovementService(session).get_run(current_user.id, document_id, run_id)
    return ApiResponse(success=True, data=run, message="지원 문서 개선 실행 상세입니다.")


@router.post("/{document_id}/improvements/{run_id}/retry", response_model=ApiResponse[DocumentImprovementRunPublic], status_code=status.HTTP_201_CREATED)
async def retry_document_improvement(
    document_id: int,
    run_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[DocumentImprovementRunPublic]:
    run = await DocumentImprovementService(session).retry_run(current_user.id, document_id, run_id)
    return ApiResponse(success=True, data=run, message="지원 문서 개선 생성을 재시도했습니다.")


@router.delete("/{document_id}/improvements/{run_id}", response_model=ApiResponse[DocumentImprovementDeletedData])
async def delete_document_improvement(
    document_id: int,
    run_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[DocumentImprovementDeletedData]:
    data = await DocumentImprovementService(session).delete_run(current_user.id, document_id, run_id)
    return ApiResponse(success=True, data=data, message="지원 문서 개선 실행이 삭제되었습니다.")


@router.patch("/{document_id}/improvements/{run_id}/suggestions/{suggestion_id}", response_model=ApiResponse[DocumentImprovementSuggestionPublic])
async def update_document_improvement_suggestion(
    document_id: int,
    run_id: int,
    suggestion_id: int,
    payload: DocumentImprovementSuggestionUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[DocumentImprovementSuggestionPublic]:
    suggestion = await DocumentImprovementService(session).update_suggestion(current_user.id, document_id, run_id, suggestion_id, payload)
    return ApiResponse(success=True, data=suggestion, message="지원 문서 개선 제안 상태가 변경되었습니다.")


@router.post("/{document_id}/improvements/{run_id}/apply", response_model=ApiResponse[DocumentImprovementApplyData])
async def apply_document_improvement(
    document_id: int,
    run_id: int,
    payload: DocumentImprovementApplyRequest = DocumentImprovementApplyRequest(),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[DocumentImprovementApplyData]:
    data = await DocumentImprovementService(session).apply_run(current_user.id, document_id, run_id, payload)
    return ApiResponse(success=True, data=data, message="지원 문서 개선안이 새 버전으로 적용되었습니다.")


@router.post("/{document_id}/improvements/{run_id}/reject", response_model=ApiResponse[DocumentImprovementRejectData])
async def reject_document_improvement(
    document_id: int,
    run_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[DocumentImprovementRejectData]:
    data = await DocumentImprovementService(session).reject_run(current_user.id, document_id, run_id)
    return ApiResponse(success=True, data=data, message="지원 문서 개선 실행이 거절되었습니다.")
