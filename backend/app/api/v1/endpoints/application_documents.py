from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_session
from app.models.application_document import ApplicationDocumentStatus, ApplicationDocumentType
from app.models.user import User
from app.schemas.application_document import (
    ApplicationDocumentCreate,
    ApplicationDocumentDuplicateRequest,
    ApplicationDocumentGenerateRequest,
    ApplicationDocumentListData,
    ApplicationDocumentPublic,
    ApplicationDocumentSourcePublic,
    ApplicationDocumentUpdate,
    ApplicationDocumentVersionCreate,
    ApplicationDocumentVersionPublic,
    GenerationRunPublic,
)
from app.schemas.common import ApiResponse
from app.services.application_document import ApplicationDocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=ApiResponse[ApplicationDocumentPublic], status_code=status.HTTP_201_CREATED)
async def create_document(
    payload: ApplicationDocumentCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationDocumentPublic]:
    service = ApplicationDocumentService(session)
    document = await service.create_document(current_user.id, payload)
    return ApiResponse(success=True, data=service._to_public(document), message="지원 문서가 생성되었습니다.")


@router.get("", response_model=ApiResponse[ApplicationDocumentListData])
async def list_documents(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    document_type: ApplicationDocumentType | None = None,
    status_filter: ApplicationDocumentStatus | None = Query(default=None, alias="status"),
    job_id: int | None = None,
    resume_id: int | None = None,
    keyword: str | None = None,
    include_archived: bool = False,
) -> ApiResponse[ApplicationDocumentListData]:
    data = await ApplicationDocumentService(session).list_documents(
        current_user.id,
        page=page,
        size=size,
        document_type=document_type,
        status=status_filter,
        job_id=job_id,
        resume_id=resume_id,
        keyword=keyword,
        include_archived=include_archived,
    )
    return ApiResponse(success=True, data=data, message="지원 문서 목록입니다.")


@router.get("/{document_id}", response_model=ApiResponse[ApplicationDocumentPublic])
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationDocumentPublic]:
    service = ApplicationDocumentService(session)
    document = await service.get_document(current_user.id, document_id)
    return ApiResponse(success=True, data=service._to_public(document), message="지원 문서 상세입니다.")


@router.patch("/{document_id}", response_model=ApiResponse[ApplicationDocumentPublic])
async def update_document(
    document_id: int,
    payload: ApplicationDocumentUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationDocumentPublic]:
    service = ApplicationDocumentService(session)
    document = await service.update_document(current_user.id, document_id, payload)
    return ApiResponse(success=True, data=service._to_public(document), message="지원 문서가 수정되었습니다.")


@router.delete("/{document_id}", response_model=ApiResponse[dict[str, bool]])
async def archive_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, bool]]:
    data = await ApplicationDocumentService(session).archive_document(current_user.id, document_id)
    return ApiResponse(success=True, data=data, message="지원 문서가 보관되었습니다.")


@router.post("/{document_id}/generate", response_model=ApiResponse[ApplicationDocumentPublic])
async def generate_document(
    document_id: int,
    payload: ApplicationDocumentGenerateRequest = ApplicationDocumentGenerateRequest(),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationDocumentPublic]:
    service = ApplicationDocumentService(session)
    document = await service.generate(current_user.id, document_id, payload)
    return ApiResponse(success=True, data=service._to_public(document), message="지원 문서 초안이 생성되었습니다.")


@router.post("/{document_id}/regenerate", response_model=ApiResponse[ApplicationDocumentPublic])
async def regenerate_document(
    document_id: int,
    payload: ApplicationDocumentGenerateRequest = ApplicationDocumentGenerateRequest(),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationDocumentPublic]:
    service = ApplicationDocumentService(session)
    document = await service.generate(current_user.id, document_id, payload)
    return ApiResponse(success=True, data=service._to_public(document), message="지원 문서 초안이 재생성되었습니다.")


@router.get("/{document_id}/versions", response_model=ApiResponse[list[ApplicationDocumentVersionPublic]])
async def list_versions(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ApplicationDocumentVersionPublic]]:
    versions = await ApplicationDocumentService(session).list_versions(current_user.id, document_id)
    return ApiResponse(success=True, data=[ApplicationDocumentVersionPublic.model_validate(v) for v in versions], message="문서 버전 목록입니다.")


@router.get("/{document_id}/versions/{version_id}", response_model=ApiResponse[ApplicationDocumentVersionPublic])
async def get_version(
    document_id: int,
    version_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationDocumentVersionPublic]:
    version = await ApplicationDocumentService(session).get_version(current_user.id, document_id, version_id)
    return ApiResponse(success=True, data=ApplicationDocumentVersionPublic.model_validate(version), message="문서 버전 상세입니다.")


@router.post("/{document_id}/versions", response_model=ApiResponse[ApplicationDocumentVersionPublic], status_code=status.HTTP_201_CREATED)
async def create_version(
    document_id: int,
    payload: ApplicationDocumentVersionCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationDocumentVersionPublic]:
    version = await ApplicationDocumentService(session).create_user_version(current_user.id, document_id, payload)
    return ApiResponse(success=True, data=ApplicationDocumentVersionPublic.model_validate(version), message="사용자 편집 버전이 저장되었습니다.")


@router.post("/{document_id}/versions/{version_id}/restore", response_model=ApiResponse[ApplicationDocumentVersionPublic])
async def restore_version(
    document_id: int,
    version_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationDocumentVersionPublic]:
    version = await ApplicationDocumentService(session).restore_version(current_user.id, document_id, version_id)
    return ApiResponse(success=True, data=ApplicationDocumentVersionPublic.model_validate(version), message="문서 버전이 복원되었습니다.")


@router.get("/{document_id}/sources", response_model=ApiResponse[list[ApplicationDocumentSourcePublic]])
async def list_sources(
    document_id: int,
    version_id: int | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ApplicationDocumentSourcePublic]]:
    sources = await ApplicationDocumentService(session).list_sources(current_user.id, document_id, version_id)
    return ApiResponse(success=True, data=[ApplicationDocumentSourcePublic.model_validate(s) for s in sources], message="문서 근거 목록입니다.")


@router.get("/{document_id}/generation-runs", response_model=ApiResponse[list[GenerationRunPublic]])
async def list_generation_runs(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[GenerationRunPublic]]:
    runs = await ApplicationDocumentService(session).list_generation_runs(current_user.id, document_id)
    return ApiResponse(success=True, data=[GenerationRunPublic.model_validate(r) for r in runs], message="생성 실행 이력입니다.")


@router.get("/{document_id}/generation-runs/{run_id}", response_model=ApiResponse[GenerationRunPublic])
async def get_generation_run(
    document_id: int,
    run_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[GenerationRunPublic]:
    run = await ApplicationDocumentService(session).get_generation_run(current_user.id, document_id, run_id)
    return ApiResponse(success=True, data=GenerationRunPublic.model_validate(run), message="생성 실행 상세입니다.")


@router.post("/{document_id}/duplicate", response_model=ApiResponse[ApplicationDocumentPublic], status_code=status.HTTP_201_CREATED)
async def duplicate_document(
    document_id: int,
    payload: ApplicationDocumentDuplicateRequest = ApplicationDocumentDuplicateRequest(),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationDocumentPublic]:
    service = ApplicationDocumentService(session)
    document = await service.duplicate_document(current_user.id, document_id, payload)
    return ApiResponse(success=True, data=service._to_public(document), message="지원 문서가 복제되었습니다.")
