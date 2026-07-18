from fastapi import APIRouter, status

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

    return ApiResponse(
        success=True,
        data=HealthData(
            status="UP",
            database=database_status,
            redis=redis_status,
        ),
        message="서비스가 정상적으로 실행 중입니다.",
    )
