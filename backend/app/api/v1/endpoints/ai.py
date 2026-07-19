from fastapi import APIRouter, Depends

from app.ai.providers import provider_status
from app.api.deps.auth import get_current_user
from app.core.config import get_settings
from app.models.user import User
from app.schemas.application_document import DocumentProviderStatus
from app.schemas.common import ApiResponse
from app.schemas.job_analysis import AIProviderStatusData

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/providers", response_model=ApiResponse[AIProviderStatusData])
async def get_ai_providers(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[AIProviderStatusData]:
    _ = current_user
    data = AIProviderStatusData.model_validate(provider_status(get_settings()))
    return ApiResponse(success=True, data=data, message="AI Provider status.")


@router.get("/resume-providers", response_model=ApiResponse[AIProviderStatusData])
async def get_resume_ai_providers(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[AIProviderStatusData]:
    _ = current_user
    data = AIProviderStatusData.model_validate(provider_status(get_settings()))
    return ApiResponse(success=True, data=data, message="Resume AI Provider status.")


@router.get("/document-providers", response_model=ApiResponse[DocumentProviderStatus])
async def get_document_ai_providers(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[DocumentProviderStatus]:
    _ = current_user
    status = provider_status(get_settings())
    data = DocumentProviderStatus(
        active_provider=str(status["active_provider"]),
        enabled=bool(status["enabled"]),
        model=status["model"] if isinstance(status["model"], str) or status["model"] is None else None,
        generation_available=bool(status.get("generation_available", status["analysis_available"])),
    )
    return ApiResponse(success=True, data=data, message="Application document AI Provider status.")
