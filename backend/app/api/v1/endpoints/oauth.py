from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.api.v1.endpoints.auth import set_refresh_cookie
from app.core.config import settings
from app.core.exceptions import AppError
from app.db.session import get_session
from app.models.oauth import OAuthPurpose
from app.models.user import User
from app.schemas.auth import UserPublic
from app.schemas.common import ApiResponse
from app.schemas.oauth import (
    OAuthAccountsData,
    OAuthAuthorizationData,
    OAuthExchangeData,
    OAuthExchangeRequest,
    OAuthProviderPublic,
    OAuthProvidersData,
)
from app.services.oauth import OAuthService, frontend_callback_url, provider_from_path

router = APIRouter(prefix="/auth/oauth", tags=["auth"])


@router.get("/providers", response_model=ApiResponse[OAuthProvidersData])
async def providers(
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[OAuthProvidersData]:
    items = [OAuthProviderPublic(**item) for item in OAuthService(session).providers()]
    return ApiResponse(
        success=True,
        data=OAuthProvidersData(providers=items),
        message="OAuth provider list returned.",
    )


@router.get("/{provider}/authorize", response_model=ApiResponse[OAuthAuthorizationData])
async def authorize(
    provider: str,
    redirect_path: str = Query(default="/me"),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[OAuthAuthorizationData]:
    authorization_url = await OAuthService(session).create_authorization_url(
        provider_from_path(provider),
        OAuthPurpose.LOGIN,
        redirect_path,
    )
    return ApiResponse(
        success=True,
        data=OAuthAuthorizationData(authorization_url=authorization_url),
        message="OAuth authorization URL created.",
    )


@router.get("/{provider}/link/authorize", response_model=ApiResponse[OAuthAuthorizationData])
async def link_authorize(
    provider: str,
    redirect_path: str = Query(default="/settings/accounts"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[OAuthAuthorizationData]:
    authorization_url = await OAuthService(session).create_authorization_url(
        provider_from_path(provider),
        OAuthPurpose.LINK,
        redirect_path,
        current_user.id,
    )
    return ApiResponse(
        success=True,
        data=OAuthAuthorizationData(authorization_url=authorization_url),
        message="OAuth link authorization URL created.",
    )


@router.get("/{provider}/callback")
async def callback(
    provider: str,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    redirect_path = "/login"
    try:
        ticket, error_code, redirect_path = await OAuthService(session).handle_callback(
            provider_from_path(provider),
            code,
            state,
            error,
        )
    except AppError as exc:
        ticket = None
        error_code = exc.code

    return RedirectResponse(
        frontend_callback_url(ticket=ticket, error=error_code, redirect_path=redirect_path),
        status_code=302,
    )


@router.post("/exchange", response_model=ApiResponse[OAuthExchangeData])
async def exchange(
    payload: OAuthExchangeRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[OAuthExchangeData]:
    (
        user,
        access_token,
        refresh_token,
        _refresh_expires_at,
        redirect_path,
        provider,
    ) = await OAuthService(session).exchange_ticket(
        payload.ticket, request.headers.get("user-agent")
    )
    max_age = settings.refresh_token_expire_days * 24 * 60 * 60
    set_refresh_cookie(response, refresh_token, max_age)
    return ApiResponse(
        success=True,
        data=OAuthExchangeData(
            access_token=access_token,
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserPublic.model_validate(user),
            redirect_path=redirect_path,
            provider=provider,
        ),
        message="OAuth login completed.",
    )


@router.get("/accounts", response_model=ApiResponse[OAuthAccountsData])
async def accounts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[OAuthAccountsData]:
    return ApiResponse(
        success=True,
        data=OAuthAccountsData(accounts=await OAuthService(session).list_accounts(current_user)),
        message="Linked OAuth accounts returned.",
    )


@router.delete("/accounts/{provider}", response_model=ApiResponse[dict[str, bool]])
async def unlink(
    provider: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, bool]]:
    await OAuthService(session).unlink_account(current_user, provider_from_path(provider))
    return ApiResponse(
        success=True,
        data={"unlinked": True},
        message="OAuth account unlinked.",
    )
