from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_session
from app.models.email_analysis import EmailCandidateStatus, EmailCandidateType
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.gmail_integration import (
    EmailCandidateApplicationOptionsData,
    EmailCandidateApproveData,
    EmailCandidateApproveRequest,
    EmailCandidateListData,
    EmailCandidatePublic,
    EmailCandidateRejectRequest,
    EmailSyncRunPublic,
    GmailCallbackData,
    GmailConnectData,
    GmailConnectRequest,
    GmailIntegrationStatusData,
    GmailSettingsUpdate,
    GmailSyncResult,
)
from app.services.gmail_integration import GmailIntegrationService

router = APIRouter(tags=["gmail-integration"])


@router.get("/integrations/gmail/status", response_model=ApiResponse[GmailIntegrationStatusData])
async def gmail_status(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[GmailIntegrationStatusData]:
    return ApiResponse(success=True, data=await GmailIntegrationService(session).status(current_user.id), message="Gmail connection status.")


@router.post("/integrations/gmail/connect", response_model=ApiResponse[GmailConnectData])
async def gmail_connect(
    payload: GmailConnectRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[GmailConnectData]:
    return ApiResponse(success=True, data=await GmailIntegrationService(session).connect(current_user.id, payload.redirect_path), message="Gmail OAuth URL created.")


@router.get("/integrations/gmail/callback", response_model=ApiResponse[GmailCallbackData])
async def gmail_callback(
    state: str | None = None,
    code: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[GmailCallbackData]:
    return ApiResponse(success=True, data=await GmailIntegrationService(session).callback(state, code), message="Gmail OAuth completed.")


@router.patch("/integrations/gmail/settings", response_model=ApiResponse[GmailIntegrationStatusData])
async def gmail_settings(
    payload: GmailSettingsUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[GmailIntegrationStatusData]:
    return ApiResponse(success=True, data=await GmailIntegrationService(session).update_settings(current_user.id, payload), message="Gmail settings updated.")


@router.delete("/integrations/gmail/connection", response_model=ApiResponse[dict[str, bool]])
async def gmail_disconnect(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, bool]]:
    return ApiResponse(success=True, data=await GmailIntegrationService(session).disconnect(current_user.id), message="Gmail disconnected.")


@router.post("/integrations/gmail/sync", response_model=ApiResponse[GmailSyncResult])
async def gmail_sync(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[GmailSyncResult]:
    return ApiResponse(success=True, data=await GmailIntegrationService(session).sync(current_user.id), message="Gmail sync completed.")


@router.get("/integrations/gmail/sync-runs", response_model=ApiResponse[list[EmailSyncRunPublic]])
async def gmail_sync_runs(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[EmailSyncRunPublic]]:
    return ApiResponse(success=True, data=await GmailIntegrationService(session).list_sync_runs(current_user.id), message="Gmail sync runs.")


@router.get("/integrations/gmail/sync-runs/{run_id}", response_model=ApiResponse[EmailSyncRunPublic])
async def gmail_sync_run_detail(
    run_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[EmailSyncRunPublic]:
    return ApiResponse(success=True, data=await GmailIntegrationService(session).get_sync_run(current_user.id, run_id), message="Gmail sync run detail.")


@router.get("/email-candidates", response_model=ApiResponse[EmailCandidateListData])
async def email_candidates(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status: EmailCandidateStatus | None = None,
    candidate_type: EmailCandidateType | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[EmailCandidateListData]:
    data = await GmailIntegrationService(session).list_candidates(current_user.id, page=page, size=size, status=status, candidate_type=candidate_type)
    return ApiResponse(success=True, data=data, message="Email candidates.")


@router.get("/email-candidates/{candidate_id}", response_model=ApiResponse[EmailCandidatePublic])
async def email_candidate_detail(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[EmailCandidatePublic]:
    return ApiResponse(success=True, data=await GmailIntegrationService(session).get_candidate(current_user.id, candidate_id), message="Email candidate detail.")


@router.post("/email-candidates/{candidate_id}/approve", response_model=ApiResponse[EmailCandidateApproveData])
async def approve_email_candidate(
    candidate_id: int,
    payload: EmailCandidateApproveRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[EmailCandidateApproveData]:
    return ApiResponse(success=True, data=await GmailIntegrationService(session).approve_candidate(current_user.id, candidate_id, payload), message="Email candidate approved.")


@router.post("/email-candidates/{candidate_id}/reject", response_model=ApiResponse[EmailCandidatePublic])
async def reject_email_candidate(
    candidate_id: int,
    payload: EmailCandidateRejectRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[EmailCandidatePublic]:
    return ApiResponse(success=True, data=await GmailIntegrationService(session).reject_candidate(current_user.id, candidate_id, payload.reason), message="Email candidate rejected.")


@router.post("/email-candidates/{candidate_id}/link-application", response_model=ApiResponse[EmailCandidatePublic])
async def link_email_candidate_application(
    candidate_id: int,
    application_id: int = Query(..., ge=1),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[EmailCandidatePublic]:
    return ApiResponse(success=True, data=await GmailIntegrationService(session).link_application(current_user.id, candidate_id, application_id), message="Application linked.")


@router.get("/email-candidates/{candidate_id}/application-options", response_model=ApiResponse[EmailCandidateApplicationOptionsData])
async def email_candidate_application_options(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[EmailCandidateApplicationOptionsData]:
    return ApiResponse(success=True, data=await GmailIntegrationService(session).application_options(current_user.id, candidate_id), message="Application options.")
