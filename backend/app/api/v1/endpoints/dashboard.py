from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.dashboard import DashboardPeriod, DashboardResponse
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=ApiResponse[DashboardResponse])
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    period: DashboardPeriod = "30d",
    start_date: date | None = None,
    end_date: date | None = None,
    timezone: str = "Asia/Seoul",
    recent_limit: int = Query(default=5, ge=1, le=20),
) -> ApiResponse[DashboardResponse]:
    data = await DashboardService(session).get_dashboard(
        current_user.id,
        period=period,
        start_date=start_date,
        end_date=end_date,
        timezone=timezone,
        recent_limit=recent_limit,
    )
    return ApiResponse(success=True, data=data, message="Dashboard summary.")
