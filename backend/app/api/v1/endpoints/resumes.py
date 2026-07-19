from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.resume import (
    ResumeCreate,
    ResumeDeletedData,
    ResumeExtractionRunListData,
    ResumeExtractionRunPublic,
    ResumeExtractionUpdate,
    ResumeFileDeletedData,
    ResumeFileExtractionPublic,
    ResumeFilePublic,
    ResumeListData,
    ResumePublic,
    ResumeUpdate,
)
from app.schemas.resume_analysis import (
    ResumeAnalysisDeletedData,
    ResumeAnalysisPublic,
    ResumeAnalysisRunRequest,
    ResumeAnalysisRunsData,
    ResumeAnalysisRunPublic,
    ResumeAnalysisUpdate,
    ResumeProfileCandidateData,
)
from app.services.resume import ResumeService
from app.services.resume_analysis import ResumeAnalysisService

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("", response_model=ApiResponse[ResumePublic], status_code=status.HTTP_201_CREATED)
async def create_resume(
    payload: ResumeCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumePublic]:
    resume = await ResumeService(session).create_resume(current_user.id, payload)
    return ApiResponse(success=True, data=ResumePublic.model_validate(resume), message="이력서가 생성되었습니다.")


@router.get("", response_model=ApiResponse[ResumeListData])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[ResumeListData]:
    data = await ResumeService(session).list_resumes(current_user.id, page, size)
    return ApiResponse(success=True, data=data, message="이력서 목록입니다.")


@router.get("/{resume_id}", response_model=ApiResponse[ResumePublic])
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumePublic]:
    resume = await ResumeService(session).get_resume(current_user.id, resume_id)
    return ApiResponse(success=True, data=ResumePublic.model_validate(resume), message="이력서 상세입니다.")


@router.patch("/{resume_id}", response_model=ApiResponse[ResumePublic])
async def update_resume(
    resume_id: int,
    payload: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumePublic]:
    resume = await ResumeService(session).update_resume(current_user.id, resume_id, payload)
    return ApiResponse(success=True, data=ResumePublic.model_validate(resume), message="이력서가 수정되었습니다.")


@router.post("/{resume_id}/default", response_model=ApiResponse[ResumePublic])
async def set_default_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumePublic]:
    resume = await ResumeService(session).set_default(current_user.id, resume_id)
    return ApiResponse(success=True, data=ResumePublic.model_validate(resume), message="기본 이력서로 설정되었습니다.")


@router.delete("/{resume_id}", response_model=ApiResponse[ResumeDeletedData])
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeDeletedData]:
    await ResumeService(session).delete_resume(current_user.id, resume_id)
    return ApiResponse(success=True, data=ResumeDeletedData(deleted=True), message="이력서가 삭제되었습니다.")


@router.post(
    "/{resume_id}/files",
    response_model=ApiResponse[ResumeFilePublic],
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume_file(
    resume_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeFilePublic]:
    resume_file = await ResumeService(session).upload_file(current_user.id, resume_id, file)
    return ApiResponse(success=True, data=ResumeFilePublic.model_validate(resume_file), message="이력서 파일이 업로드되었습니다.")


@router.get("/{resume_id}/files/{file_id}", response_model=ApiResponse[ResumeFilePublic])
async def get_resume_file(
    resume_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeFilePublic]:
    resume_file = await ResumeService(session).get_file(current_user.id, resume_id, file_id)
    return ApiResponse(success=True, data=ResumeFilePublic.model_validate(resume_file), message="이력서 파일 상세입니다.")


@router.get("/{resume_id}/files/{file_id}/download")
async def download_resume_file(
    resume_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FileResponse:
    service = ResumeService(session)
    resume_file = await service.get_file(current_user.id, resume_id, file_id)
    storage_path = service.storage.existing_file_path(resume_file.storage_path)
    quoted = quote(resume_file.original_filename)
    return FileResponse(
        storage_path,
        media_type=resume_file.content_type,
        filename=resume_file.original_filename,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quoted}",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.delete("/{resume_id}/files/{file_id}", response_model=ApiResponse[ResumeFileDeletedData])
async def delete_resume_file(
    resume_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeFileDeletedData]:
    await ResumeService(session).delete_file(current_user.id, resume_id, file_id)
    return ApiResponse(success=True, data=ResumeFileDeletedData(deleted=True), message="이력서 파일이 삭제되었습니다.")


@router.post(
    "/{resume_id}/files/{file_id}/extraction",
    response_model=ApiResponse[ResumeFileExtractionPublic],
)
async def extract_resume_file(
    resume_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeFileExtractionPublic]:
    extraction = await ResumeService(session).extract_file(current_user.id, resume_id, file_id)
    return ApiResponse(
        success=True,
        data=ResumeFileExtractionPublic.model_validate(extraction),
        message="이력서 텍스트 추출이 완료되었습니다.",
    )


@router.get(
    "/{resume_id}/files/{file_id}/extraction",
    response_model=ApiResponse[ResumeFileExtractionPublic],
)
async def get_resume_file_extraction(
    resume_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeFileExtractionPublic]:
    extraction = await ResumeService(session).get_extraction(current_user.id, resume_id, file_id)
    return ApiResponse(
        success=True,
        data=ResumeFileExtractionPublic.model_validate(extraction),
        message="이력서 텍스트 추출 결과입니다.",
    )


@router.patch(
    "/{resume_id}/files/{file_id}/extraction",
    response_model=ApiResponse[ResumeFileExtractionPublic],
)
async def update_resume_file_extraction(
    resume_id: int,
    file_id: int,
    payload: ResumeExtractionUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeFileExtractionPublic]:
    extraction = await ResumeService(session).update_extraction(current_user.id, resume_id, file_id, payload)
    return ApiResponse(
        success=True,
        data=ResumeFileExtractionPublic.model_validate(extraction),
        message="이력서 텍스트 수정본이 저장되었습니다.",
    )


@router.post(
    "/{resume_id}/files/{file_id}/extraction/retry",
    response_model=ApiResponse[ResumeFileExtractionPublic],
)
async def retry_resume_file_extraction(
    resume_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeFileExtractionPublic]:
    extraction = await ResumeService(session).extract_file(current_user.id, resume_id, file_id)
    return ApiResponse(
        success=True,
        data=ResumeFileExtractionPublic.model_validate(extraction),
        message="이력서 텍스트 재추출이 완료되었습니다.",
    )


@router.get(
    "/{resume_id}/files/{file_id}/extraction/runs",
    response_model=ApiResponse[ResumeExtractionRunListData],
)
async def list_resume_file_extraction_runs(
    resume_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeExtractionRunListData]:
    runs = await ResumeService(session).list_extraction_runs(current_user.id, resume_id, file_id)
    return ApiResponse(
        success=True,
        data=ResumeExtractionRunListData(items=[ResumeExtractionRunPublic.model_validate(run) for run in runs]),
        message="이력서 텍스트 추출 실행 이력입니다.",
    )


@router.get(
    "/{resume_id}/files/{file_id}/extraction/runs/{run_id}",
    response_model=ApiResponse[ResumeExtractionRunPublic],
)
async def get_resume_file_extraction_run(
    resume_id: int,
    file_id: int,
    run_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeExtractionRunPublic]:
    run = await ResumeService(session).get_extraction_run(current_user.id, resume_id, file_id, run_id)
    return ApiResponse(
        success=True,
        data=ResumeExtractionRunPublic.model_validate(run),
        message="이력서 텍스트 추출 실행 이력 상세입니다.",
    )


@router.post(
    "/{resume_id}/files/{file_id}/analysis",
    response_model=ApiResponse[ResumeAnalysisPublic],
)
async def analyze_resume_file(
    resume_id: int,
    file_id: int,
    payload: ResumeAnalysisRunRequest | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeAnalysisPublic]:
    data = await ResumeAnalysisService(session).analyze_resume(
        current_user.id,
        resume_id,
        file_id,
        force=payload.force if payload else False,
    )
    return ApiResponse(success=True, data=data, message="이력서 AI 분석이 완료되었습니다.")


@router.get(
    "/{resume_id}/files/{file_id}/analysis",
    response_model=ApiResponse[ResumeAnalysisPublic],
)
async def get_resume_file_analysis(
    resume_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeAnalysisPublic]:
    data = await ResumeAnalysisService(session).get_analysis(current_user.id, resume_id, file_id)
    return ApiResponse(success=True, data=data, message="이력서 AI 분석 결과입니다.")


@router.patch(
    "/{resume_id}/files/{file_id}/analysis",
    response_model=ApiResponse[ResumeAnalysisPublic],
)
async def update_resume_file_analysis(
    resume_id: int,
    file_id: int,
    payload: ResumeAnalysisUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeAnalysisPublic]:
    data = await ResumeAnalysisService(session).update_analysis(current_user.id, resume_id, file_id, payload)
    return ApiResponse(success=True, data=data, message="이력서 AI 분석 수정본이 저장되었습니다.")


@router.delete(
    "/{resume_id}/files/{file_id}/analysis",
    response_model=ApiResponse[ResumeAnalysisDeletedData],
)
async def delete_resume_file_analysis(
    resume_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeAnalysisDeletedData]:
    data = await ResumeAnalysisService(session).delete_analysis(current_user.id, resume_id, file_id)
    return ApiResponse(success=True, data=data, message="이력서 AI 분석 결과가 삭제되었습니다.")


@router.post(
    "/{resume_id}/files/{file_id}/analysis/retry",
    response_model=ApiResponse[ResumeAnalysisPublic],
)
async def retry_resume_file_analysis(
    resume_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeAnalysisPublic]:
    data = await ResumeAnalysisService(session).analyze_resume(current_user.id, resume_id, file_id, force=True)
    return ApiResponse(success=True, data=data, message="이력서 AI 분석이 재실행되었습니다.")


@router.get(
    "/{resume_id}/files/{file_id}/analysis/runs",
    response_model=ApiResponse[ResumeAnalysisRunsData],
)
async def list_resume_file_analysis_runs(
    resume_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[ResumeAnalysisRunsData]:
    data = await ResumeAnalysisService(session).list_runs(current_user.id, resume_id, file_id, page, size)
    return ApiResponse(success=True, data=data, message="이력서 AI 분석 실행 이력입니다.")


@router.get(
    "/{resume_id}/files/{file_id}/analysis/runs/{run_id}",
    response_model=ApiResponse[ResumeAnalysisRunPublic],
)
async def get_resume_file_analysis_run(
    resume_id: int,
    file_id: int,
    run_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeAnalysisRunPublic]:
    data = await ResumeAnalysisService(session).get_run(current_user.id, resume_id, file_id, run_id)
    return ApiResponse(success=True, data=data, message="이력서 AI 분석 실행 이력 상세입니다.")


@router.get(
    "/{resume_id}/files/{file_id}/analysis/profile-candidates",
    response_model=ApiResponse[ResumeProfileCandidateData],
)
async def get_resume_file_analysis_profile_candidates(
    resume_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ResumeProfileCandidateData]:
    data = await ResumeAnalysisService(session).get_profile_candidates(current_user.id, resume_id, file_id)
    return ApiResponse(success=True, data=data, message="프로필 반영 후보입니다.")
