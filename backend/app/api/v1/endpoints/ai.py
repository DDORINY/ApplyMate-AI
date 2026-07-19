from fastapi import APIRouter, Depends

from app.ai.providers import provider_status
from app.api.deps.auth import get_current_user
from app.core.config import get_settings
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.job_analysis import AIProviderStatusData

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/providers", response_model=ApiResponse[AIProviderStatusData])
async def get_ai_providers(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[AIProviderStatusData]:
    _ = current_user
    data = AIProviderStatusData.model_validate(provider_status(get_settings()))
    return ApiResponse(success=True, data=data, message="AI Provider 상태입니다.")
