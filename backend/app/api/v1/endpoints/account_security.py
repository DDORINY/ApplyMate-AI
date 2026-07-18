from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.api.v1.endpoints.auth import clear_refresh_cookie, client_ip
from app.core.security import REFRESH_TOKEN_COOKIE_NAME
from app.db.session import get_session
from app.models.user import User
from app.schemas.account_security import (
    EmailVerificationSendData,
    EmailVerificationVerifyRequest,
    ForgotPasswordData,
    ForgotPasswordRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordSetRequest,
    PasswordUpdatedData,
    SecurityEventPublic,
    SecurityEventsData,
    SessionRevokedData,
    SessionsData,
)
from app.schemas.auth import UserPublic
from app.schemas.common import ApiResponse
from app.services.account_security import AccountSecurityService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/email-verification/send", response_model=ApiResponse[EmailVerificationSendData])
async def send_email_verification(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[EmailVerificationSendData]:
    await AccountSecurityService(session).send_email_verification(
        current_user,
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip(request),
    )
    return ApiResponse(
        success=True,
        data=EmailVerificationSendData(sent=True, email=current_user.email),
        message="이메일 인증 메일을 발송했습니다.",
    )


@router.post("/email-verification/verify", response_model=ApiResponse[UserPublic])
async def verify_email(
    payload: EmailVerificationVerifyRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[UserPublic]:
    user = await AccountSecurityService(session).verify_email(
        payload.token,
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip(request),
    )
    return ApiResponse(
        success=True,
        data=UserPublic.model_validate(user),
        message="이메일 인증이 완료되었습니다.",
    )


@router.post("/password/forgot", response_model=ApiResponse[ForgotPasswordData])
async def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ForgotPasswordData]:
    await AccountSecurityService(session).request_password_reset(
        payload.email,
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip(request),
    )
    return ApiResponse(
        success=True,
        data=ForgotPasswordData(accepted=True),
        message="계정이 존재하면 비밀번호 재설정 안내 메일을 발송합니다.",
    )


@router.post("/password/reset", response_model=ApiResponse[PasswordUpdatedData])
async def reset_password(
    payload: PasswordResetRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[PasswordUpdatedData]:
    await AccountSecurityService(session).reset_password(
        payload.token,
        payload.new_password,
        payload.new_password_confirm,
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip(request),
    )
    clear_refresh_cookie(response)
    return ApiResponse(
        success=True,
        data=PasswordUpdatedData(updated=True),
        message="비밀번호가 재설정되었습니다. 다시 로그인해 주세요.",
    )


@router.post("/password/change", response_model=ApiResponse[PasswordUpdatedData])
async def change_password(
    payload: PasswordChangeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[PasswordUpdatedData]:
    await AccountSecurityService(session).change_password(
        current_user,
        payload.current_password,
        payload.new_password,
        payload.new_password_confirm,
        refresh_token=request.cookies.get(REFRESH_TOKEN_COOKIE_NAME),
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip(request),
    )
    return ApiResponse(
        success=True,
        data=PasswordUpdatedData(updated=True),
        message="비밀번호가 변경되었습니다. 다른 세션은 로그아웃되었습니다.",
    )


@router.post("/password/set", response_model=ApiResponse[PasswordUpdatedData])
async def set_password(
    payload: PasswordSetRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[PasswordUpdatedData]:
    await AccountSecurityService(session).set_password(
        current_user,
        payload.new_password,
        payload.new_password_confirm,
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip(request),
    )
    return ApiResponse(
        success=True,
        data=PasswordUpdatedData(updated=True),
        message="비밀번호가 설정되었습니다.",
    )


@router.get("/sessions", response_model=ApiResponse[SessionsData])
async def list_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[SessionsData]:
    sessions = await AccountSecurityService(session).list_sessions(
        current_user,
        request.cookies.get(REFRESH_TOKEN_COOKIE_NAME),
    )
    return ApiResponse(
        success=True,
        data=SessionsData(sessions=sessions),
        message="로그인 세션 목록입니다.",
    )


@router.delete("/sessions/others", response_model=ApiResponse[SessionRevokedData])
async def revoke_other_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[SessionRevokedData]:
    revoked_count = await AccountSecurityService(session).revoke_other_sessions(
        current_user,
        request.cookies.get(REFRESH_TOKEN_COOKIE_NAME),
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip(request),
    )
    return ApiResponse(
        success=True,
        data=SessionRevokedData(revoked=True, revoked_count=revoked_count),
        message="다른 세션이 로그아웃되었습니다.",
    )


@router.delete("/sessions", response_model=ApiResponse[SessionRevokedData])
async def revoke_all_sessions(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[SessionRevokedData]:
    revoked_count = await AccountSecurityService(session).revoke_all_sessions(
        current_user,
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip(request),
    )
    clear_refresh_cookie(response)
    return ApiResponse(
        success=True,
        data=SessionRevokedData(revoked=True, revoked_count=revoked_count),
        message="모든 세션이 로그아웃되었습니다.",
    )


@router.delete("/sessions/{session_id}", response_model=ApiResponse[SessionRevokedData])
async def revoke_session(
    session_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[SessionRevokedData]:
    revoked_count = await AccountSecurityService(session).revoke_session(
        current_user,
        session_id,
        refresh_token=request.cookies.get(REFRESH_TOKEN_COOKIE_NAME),
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip(request),
    )
    return ApiResponse(
        success=True,
        data=SessionRevokedData(revoked=True, revoked_count=revoked_count),
        message="선택한 세션이 로그아웃되었습니다.",
    )


@router.get("/security-events", response_model=ApiResponse[SecurityEventsData])
async def list_security_events(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[SecurityEventsData]:
    events = await AccountSecurityService(session).list_security_events(current_user)
    return ApiResponse(
        success=True,
        data=SecurityEventsData(
            events=[SecurityEventPublic.model_validate(event) for event in events]
        ),
        message="최근 보안 이벤트 목록입니다.",
    )
