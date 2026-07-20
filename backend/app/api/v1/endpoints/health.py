from fastapi import APIRouter, Response, status

from app.core.config import settings
from app.db.session import check_database, check_redis
from app.schemas.common import ApiResponse, HealthData

router = APIRouter()


@router.get(
    "/health",
    response_model=ApiResponse[HealthData],
    status_code=status.HTTP_200_OK,
)
async def health_check() -> ApiResponse[HealthData]:
    database_status = await check_database()
    redis_status = await check_redis()
    required_settings_status = check_required_settings()
    return build_health_response(database_status, redis_status, required_settings_status)


@router.get("/health/live", response_model=ApiResponse[dict[str, str]])
async def liveness_check() -> ApiResponse[dict[str, str]]:
    return ApiResponse(success=True, data={"status": "UP"}, message="서비스 프로세스가 실행 중입니다.")


@router.get("/health/ready", response_model=ApiResponse[HealthData])
async def readiness_check(response: Response) -> ApiResponse[HealthData]:
    database_status = await check_database()
    redis_status = await check_redis()
    required_settings_status = check_required_settings()
    overall = "UP" if {database_status, redis_status, required_settings_status} == {"UP"} else "DOWN"
    if overall == "DOWN":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return build_health_response(database_status, redis_status, required_settings_status)


def build_health_response(
    database_status: str, redis_status: str, required_settings_status: str
) -> ApiResponse[HealthData]:
    overall = "UP" if {database_status, redis_status, required_settings_status} == {"UP"} else "DOWN"
    return ApiResponse(
        success=True,
        data=HealthData(
            status=overall,
            database=database_status,
            redis=redis_status,
            required_settings=required_settings_status,
        ),
        message="서비스가 정상적으로 실행 중입니다.",
    )


def check_required_settings() -> str:
    if settings.app_env.lower() in {"production", "prod"}:
        required_values = [
            settings.database_url,
            settings.redis_url,
            settings.jwt_secret_key,
            settings.jwt_refresh_secret_key,
            settings.frontend_url,
            settings.backend_url,
        ]
        if not all(required_values):
            return "DOWN"
        if "*" in settings.cors_allowed_origins:
            return "DOWN"
        if settings.email_provider == "smtp" and not all(
            [settings.smtp_host, settings.smtp_username, settings.smtp_password, settings.email_from_address]
        ):
            return "DOWN"
        if settings.calendar_provider == "google" and not all(
            [
                settings.google_calendar_client_id,
                settings.google_calendar_client_secret,
                settings.external_token_encryption_key,
            ]
        ):
            return "DOWN"
        if settings.gmail_provider == "google" and not all(
            [
                settings.google_gmail_client_id,
                settings.google_gmail_client_secret,
                settings.external_token_encryption_key,
            ]
        ):
            return "DOWN"
    return "UP"
