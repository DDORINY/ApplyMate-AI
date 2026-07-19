from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_session
from app.models.application import ApplicationChannel, ApplicationPriority, ApplicationStatus
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationListData,
    ApplicationNoteCreate,
    ApplicationNotePublic,
    ApplicationNoteUpdate,
    ApplicationOptionsData,
    ApplicationPublic,
    ApplicationStatusChange,
    ApplicationStatusHistoryPublic,
    ApplicationUpdate,
)
from app.schemas.common import ApiResponse
from app.services.application import ApplicationService

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/options", response_model=ApiResponse[ApplicationOptionsData])
async def application_options(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationOptionsData]:
    data = await ApplicationService(session).options(current_user.id)
    return ApiResponse(success=True, data=data, message="지원 항목 선택 옵션입니다.")


@router.post("", response_model=ApiResponse[ApplicationPublic], status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationPublic]:
    service = ApplicationService(session)
    application = await service.create_application(current_user.id, payload)
    return ApiResponse(success=True, data=service._to_public(application), message="지원 항목이 생성되었습니다.")


@router.get("", response_model=ApiResponse[ApplicationListData])
async def list_applications(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = None,
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    company: str | None = None,
    job_id: int | None = None,
    priority: ApplicationPriority | None = None,
    application_channel: ApplicationChannel | None = None,
    applied_from: datetime | None = None,
    applied_to: datetime | None = None,
    updated_from: datetime | None = None,
    updated_to: datetime | None = None,
    has_document: bool | None = None,
    has_resume: bool | None = None,
    archived: bool = False,
    sort: str = "updated_at",
    order: str = "desc",
) -> ApiResponse[ApplicationListData]:
    data = await ApplicationService(session).list_applications(
        current_user.id,
        page=page,
        size=size,
        keyword=keyword,
        status=status_filter,
        company=company,
        job_id=job_id,
        priority=priority,
        application_channel=application_channel,
        applied_from=applied_from,
        applied_to=applied_to,
        updated_from=updated_from,
        updated_to=updated_to,
        has_document=has_document,
        has_resume=has_resume,
        archived=archived,
        sort=sort,
        order=order,
    )
    return ApiResponse(success=True, data=data, message="지원 현황 목록입니다.")


@router.get("/{application_id}", response_model=ApiResponse[ApplicationPublic])
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationPublic]:
    service = ApplicationService(session)
    application = await service.get_application(current_user.id, application_id)
    return ApiResponse(success=True, data=service._to_public(application), message="지원 항목 상세입니다.")


@router.patch("/{application_id}", response_model=ApiResponse[ApplicationPublic])
async def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationPublic]:
    service = ApplicationService(session)
    application = await service.update_application(current_user.id, application_id, payload)
    return ApiResponse(success=True, data=service._to_public(application), message="지원 항목이 수정되었습니다.")


@router.delete("/{application_id}", response_model=ApiResponse[dict[str, bool]])
async def archive_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, bool]]:
    data = await ApplicationService(session).archive_application(current_user.id, application_id)
    return ApiResponse(success=True, data=data, message="지원 항목이 보관되었습니다.")


@router.post("/{application_id}/status", response_model=ApiResponse[ApplicationPublic])
async def change_application_status(
    application_id: int,
    payload: ApplicationStatusChange,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationPublic]:
    service = ApplicationService(session)
    application = await service.change_status(current_user.id, application_id, payload)
    return ApiResponse(success=True, data=service._to_public(application), message="지원 상태가 변경되었습니다.")


@router.get("/{application_id}/status-history", response_model=ApiResponse[list[ApplicationStatusHistoryPublic]])
async def list_application_status_history(
    application_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ApplicationStatusHistoryPublic]]:
    data = await ApplicationService(session).list_status_history(current_user.id, application_id)
    return ApiResponse(success=True, data=data, message="지원 상태 변경 이력입니다.")


@router.post("/{application_id}/notes", response_model=ApiResponse[ApplicationNotePublic], status_code=status.HTTP_201_CREATED)
async def create_application_note(
    application_id: int,
    payload: ApplicationNoteCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationNotePublic]:
    note = await ApplicationService(session).create_note(current_user.id, application_id, payload)
    return ApiResponse(success=True, data=ApplicationNotePublic.model_validate(note), message="지원 메모가 생성되었습니다.")


@router.get("/{application_id}/notes", response_model=ApiResponse[list[ApplicationNotePublic]])
async def list_application_notes(
    application_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ApplicationNotePublic]]:
    data = await ApplicationService(session).list_notes(current_user.id, application_id)
    return ApiResponse(success=True, data=data, message="지원 메모 목록입니다.")


@router.patch("/{application_id}/notes/{note_id}", response_model=ApiResponse[ApplicationNotePublic])
async def update_application_note(
    application_id: int,
    note_id: int,
    payload: ApplicationNoteUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationNotePublic]:
    note = await ApplicationService(session).update_note(current_user.id, application_id, note_id, payload)
    return ApiResponse(success=True, data=ApplicationNotePublic.model_validate(note), message="지원 메모가 수정되었습니다.")


@router.delete("/{application_id}/notes/{note_id}", response_model=ApiResponse[dict[str, bool]])
async def delete_application_note(
    application_id: int,
    note_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, bool]]:
    data = await ApplicationService(session).delete_note(current_user.id, application_id, note_id)
    return ApiResponse(success=True, data=data, message="지원 메모가 삭제되었습니다.")
