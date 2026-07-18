from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.security import decode_jwt
from app.db.session import get_session
from app.models.user import User
from app.services.auth import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    if credentials is None:
        raise AppError("AUTH_TOKEN_MISSING", "인증 토큰이 필요합니다.", 401)
    if credentials.scheme.lower() != "bearer":
        raise AppError("AUTH_TOKEN_INVALID", "유효하지 않은 토큰입니다.", 401)

    payload = decode_jwt(credentials.credentials, "access")
    return await AuthService(session).get_active_user(int(payload["sub"]))
