from fastapi import APIRouter

from app.api.v1.endpoints.account_security import router as account_security_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.oauth import router as oauth_router
from app.api.v1.endpoints.profiles import router as profiles_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(account_security_router)
api_router.include_router(health_router, tags=["health"])
api_router.include_router(oauth_router)
api_router.include_router(profiles_router)
