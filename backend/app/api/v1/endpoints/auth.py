from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.core.config import settings
from app.core.security import REFRESH_TOKEN_COOKIE_NAME
from app.db.session import get_session
from app.models.user import User
from app.schemas.auth import AuthTokenData, LoginRequest, SignupRequest, UserPublic
from app.schemas.common import ApiResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def set_refresh_cookie(response: Response, token: str, max_age_seconds: int) -> None:
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=token,
        max_age=max_age_seconds,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/api/v1/auth",
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_TOKEN_COOKIE_NAME, path="/api/v1/auth")


@router.post("/signup", response_model=ApiResponse[UserPublic], status_code=status.HTTP_201_CREATED)
async def signup(
    payload: SignupRequest, session: AsyncSession = Depends(get_session)
) -> ApiResponse[UserPublic]:
    user = await AuthService(session).signup(payload.email, payload.password, payload.name)
    return ApiResponse(
        success=True, data=UserPublic.model_validate(user), message="회원가입이 완료되었습니다."
    )


@router.post("/login", response_model=ApiResponse[AuthTokenData])
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[AuthTokenData]:
    user, access_token, refresh_token, refresh_expires_at = await AuthService(session).login(
        payload.email,
        payload.password,
        request.headers.get("user-agent"),
    )
    max_age = settings.refresh_token_expire_days * 24 * 60 * 60
    set_refresh_cookie(response, refresh_token, max_age)
    return ApiResponse(
        success=True,
        data=AuthTokenData(
            access_token=access_token,
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserPublic.model_validate(user),
        ),
        message="로그인되었습니다.",
    )


@router.post("/refresh", response_model=ApiResponse[AuthTokenData])
async def refresh(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[AuthTokenData]:
    user, access_token, refresh_token, _refresh_expires_at = await AuthService(session).refresh(
        request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    )
    set_refresh_cookie(response, refresh_token, settings.refresh_token_expire_days * 24 * 60 * 60)
    return ApiResponse(
        success=True,
        data=AuthTokenData(
            access_token=access_token,
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserPublic.model_validate(user),
        ),
        message="Access Token이 재발급되었습니다.",
    )


@router.post("/logout", response_model=ApiResponse[dict[str, bool]])
async def logout(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, bool]]:
    await AuthService(session).logout(request.cookies.get(REFRESH_TOKEN_COOKIE_NAME))
    clear_refresh_cookie(response)
    return ApiResponse(success=True, data={"logged_out": True}, message="로그아웃되었습니다.")


@router.get("/me", response_model=ApiResponse[UserPublic])
async def me(current_user: User = Depends(get_current_user)) -> ApiResponse[UserPublic]:
    return ApiResponse(
        success=True,
        data=UserPublic.model_validate(current_user),
        message="현재 로그인 사용자입니다.",
    )
