from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.profile import (
    CareerProfileCreate,
    CareerProfilePublic,
    CareerProfileUpdate,
    ExcludedConditionCreate,
    ExcludedConditionPublic,
    ExcludedConditionUpdate,
    ExperienceCreate,
    ExperiencePublic,
    ExperienceUpdate,
    JobPreferencePayload,
    JobPreferencePublic,
    PortfolioLinkCreate,
    PortfolioLinkPublic,
    PortfolioLinkUpdate,
    ProjectCreate,
    ProjectPublic,
    ProjectUpdate,
    SkillPublic,
    UserSkillCreate,
    UserSkillPublic,
    UserSkillUpdate,
)
from app.services.profile import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


def project_public(project) -> ProjectPublic:
    return ProjectPublic(
        id=project.id,
        user_id=project.user_id,
        name=project.name,
        summary=project.summary,
        role=project.role,
        start_date=project.start_date,
        end_date=project.end_date,
        is_ongoing=project.is_ongoing,
        description=project.description,
        responsibilities=project.responsibilities,
        achievements=project.achievements,
        repository_url=project.repository_url,
        service_url=project.service_url,
        skills=[SkillPublic.model_validate(item.skill) for item in project.project_skills],
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("/me", response_model=ApiResponse[CareerProfilePublic])
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[CareerProfilePublic]:
    profile = await ProfileService(session).get_profile(current_user.id)
    return ApiResponse(
        success=True,
        data=CareerProfilePublic.model_validate(profile),
        message="커리어 프로필입니다.",
    )


@router.post(
    "", response_model=ApiResponse[CareerProfilePublic], status_code=status.HTTP_201_CREATED
)
async def create_profile(
    payload: CareerProfileCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[CareerProfilePublic]:
    profile = await ProfileService(session).create_profile(current_user.id, payload)
    return ApiResponse(
        success=True,
        data=CareerProfilePublic.model_validate(profile),
        message="커리어 프로필이 생성되었습니다.",
    )


@router.patch("/me", response_model=ApiResponse[CareerProfilePublic])
async def update_my_profile(
    payload: CareerProfileUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[CareerProfilePublic]:
    profile = await ProfileService(session).update_profile(current_user.id, payload)
    return ApiResponse(
        success=True,
        data=CareerProfilePublic.model_validate(profile),
        message="커리어 프로필이 수정되었습니다.",
    )


@router.get("/me/skills", response_model=ApiResponse[list[UserSkillPublic]])
async def list_skills(
    current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
):
    skills = await ProfileService(session).list_user_skills(current_user.id)
    return ApiResponse(
        success=True,
        data=[UserSkillPublic.model_validate(item) for item in skills],
        message="기술 목록입니다.",
    )


@router.post(
    "/me/skills", response_model=ApiResponse[UserSkillPublic], status_code=status.HTTP_201_CREATED
)
async def add_skill(
    payload: UserSkillCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    user_skill = await ProfileService(session).add_user_skill(current_user.id, payload)
    return ApiResponse(
        success=True,
        data=UserSkillPublic.model_validate(user_skill),
        message="기술이 추가되었습니다.",
    )


@router.patch("/me/skills/{user_skill_id}", response_model=ApiResponse[UserSkillPublic])
async def update_skill(
    user_skill_id: int,
    payload: UserSkillUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    user_skill = await ProfileService(session).update_user_skill(
        current_user.id, user_skill_id, payload
    )
    return ApiResponse(
        success=True,
        data=UserSkillPublic.model_validate(user_skill),
        message="기술이 수정되었습니다.",
    )


@router.delete("/me/skills/{user_skill_id}", response_model=ApiResponse[dict[str, bool]])
async def delete_skill(
    user_skill_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await ProfileService(session).delete_user_skill(current_user.id, user_skill_id)
    return ApiResponse(success=True, data={"deleted": True}, message="기술이 삭제되었습니다.")


@router.get("/me/experiences", response_model=ApiResponse[list[ExperiencePublic]])
async def list_experiences(
    current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
):
    items = await ProfileService(session).list_experiences(current_user.id)
    return ApiResponse(
        success=True,
        data=[ExperiencePublic.model_validate(item) for item in items],
        message="경력 목록입니다.",
    )


@router.post(
    "/me/experiences",
    response_model=ApiResponse[ExperiencePublic],
    status_code=status.HTTP_201_CREATED,
)
async def create_experience(
    payload: ExperienceCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    item = await ProfileService(session).create_experience(current_user.id, payload)
    return ApiResponse(
        success=True, data=ExperiencePublic.model_validate(item), message="경력이 추가되었습니다."
    )


@router.get("/me/experiences/{experience_id}", response_model=ApiResponse[ExperiencePublic])
async def get_experience(
    experience_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    item = await ProfileService(session).get_experience(current_user.id, experience_id)
    return ApiResponse(
        success=True, data=ExperiencePublic.model_validate(item), message="경력 상세입니다."
    )


@router.patch("/me/experiences/{experience_id}", response_model=ApiResponse[ExperiencePublic])
async def update_experience(
    experience_id: int,
    payload: ExperienceUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    item = await ProfileService(session).update_experience(current_user.id, experience_id, payload)
    return ApiResponse(
        success=True, data=ExperiencePublic.model_validate(item), message="경력이 수정되었습니다."
    )


@router.delete("/me/experiences/{experience_id}", response_model=ApiResponse[dict[str, bool]])
async def delete_experience(
    experience_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await ProfileService(session).delete_experience(current_user.id, experience_id)
    return ApiResponse(success=True, data={"deleted": True}, message="경력이 삭제되었습니다.")


@router.get("/me/projects", response_model=ApiResponse[list[ProjectPublic]])
async def list_projects(
    current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
):
    items = await ProfileService(session).list_projects(current_user.id)
    return ApiResponse(
        success=True, data=[project_public(item) for item in items], message="프로젝트 목록입니다."
    )


@router.post(
    "/me/projects", response_model=ApiResponse[ProjectPublic], status_code=status.HTTP_201_CREATED
)
async def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    item = await ProfileService(session).create_project(current_user.id, payload)
    return ApiResponse(
        success=True, data=project_public(item), message="프로젝트가 추가되었습니다."
    )


@router.get("/me/projects/{project_id}", response_model=ApiResponse[ProjectPublic])
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    item = await ProfileService(session).get_project(current_user.id, project_id)
    return ApiResponse(success=True, data=project_public(item), message="프로젝트 상세입니다.")


@router.patch("/me/projects/{project_id}", response_model=ApiResponse[ProjectPublic])
async def update_project(
    project_id: int,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    item = await ProfileService(session).update_project(current_user.id, project_id, payload)
    return ApiResponse(
        success=True, data=project_public(item), message="프로젝트가 수정되었습니다."
    )


@router.delete("/me/projects/{project_id}", response_model=ApiResponse[dict[str, bool]])
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await ProfileService(session).delete_project(current_user.id, project_id)
    return ApiResponse(success=True, data={"deleted": True}, message="프로젝트가 삭제되었습니다.")


@router.get("/me/preferences", response_model=ApiResponse[JobPreferencePublic])
async def get_preferences(
    current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
):
    item = await ProfileService(session).get_preferences(current_user.id)
    return ApiResponse(
        success=True, data=JobPreferencePublic.model_validate(item), message="희망 조건입니다."
    )


@router.put("/me/preferences", response_model=ApiResponse[JobPreferencePublic])
async def put_preferences(
    payload: JobPreferencePayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    item = await ProfileService(session).upsert_preferences(current_user.id, payload)
    return ApiResponse(
        success=True,
        data=JobPreferencePublic.model_validate(item),
        message="희망 조건이 저장되었습니다.",
    )


@router.patch("/me/preferences", response_model=ApiResponse[JobPreferencePublic])
async def patch_preferences(
    payload: JobPreferencePayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    item = await ProfileService(session).upsert_preferences(current_user.id, payload)
    return ApiResponse(
        success=True,
        data=JobPreferencePublic.model_validate(item),
        message="희망 조건이 수정되었습니다.",
    )


@router.get("/me/exclusions", response_model=ApiResponse[list[ExcludedConditionPublic]])
async def list_exclusions(
    current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
):
    items = await ProfileService(session).list_exclusions(current_user.id)
    return ApiResponse(
        success=True,
        data=[ExcludedConditionPublic.model_validate(item) for item in items],
        message="제외 조건 목록입니다.",
    )


@router.post(
    "/me/exclusions",
    response_model=ApiResponse[ExcludedConditionPublic],
    status_code=status.HTTP_201_CREATED,
)
async def create_exclusion(
    payload: ExcludedConditionCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    item = await ProfileService(session).create_exclusion(current_user.id, payload)
    return ApiResponse(
        success=True,
        data=ExcludedConditionPublic.model_validate(item),
        message="제외 조건이 추가되었습니다.",
    )


@router.patch("/me/exclusions/{condition_id}", response_model=ApiResponse[ExcludedConditionPublic])
async def update_exclusion(
    condition_id: int,
    payload: ExcludedConditionUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    item = await ProfileService(session).update_exclusion(current_user.id, condition_id, payload)
    return ApiResponse(
        success=True,
        data=ExcludedConditionPublic.model_validate(item),
        message="제외 조건이 수정되었습니다.",
    )


@router.delete("/me/exclusions/{condition_id}", response_model=ApiResponse[dict[str, bool]])
async def delete_exclusion(
    condition_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await ProfileService(session).delete_exclusion(current_user.id, condition_id)
    return ApiResponse(success=True, data={"deleted": True}, message="제외 조건이 삭제되었습니다.")


@router.get("/me/portfolio-links", response_model=ApiResponse[list[PortfolioLinkPublic]])
async def list_portfolio_links(
    current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
):
    items = await ProfileService(session).list_portfolio_links(current_user.id)
    return ApiResponse(
        success=True,
        data=[PortfolioLinkPublic.model_validate(item) for item in items],
        message="포트폴리오 링크 목록입니다.",
    )


@router.post(
    "/me/portfolio-links",
    response_model=ApiResponse[PortfolioLinkPublic],
    status_code=status.HTTP_201_CREATED,
)
async def create_portfolio_link(
    payload: PortfolioLinkCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    item = await ProfileService(session).create_portfolio_link(current_user.id, payload)
    return ApiResponse(
        success=True,
        data=PortfolioLinkPublic.model_validate(item),
        message="포트폴리오 링크가 추가되었습니다.",
    )


@router.patch("/me/portfolio-links/{link_id}", response_model=ApiResponse[PortfolioLinkPublic])
async def update_portfolio_link(
    link_id: int,
    payload: PortfolioLinkUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    item = await ProfileService(session).update_portfolio_link(current_user.id, link_id, payload)
    return ApiResponse(
        success=True,
        data=PortfolioLinkPublic.model_validate(item),
        message="포트폴리오 링크가 수정되었습니다.",
    )


@router.delete("/me/portfolio-links/{link_id}", response_model=ApiResponse[dict[str, bool]])
async def delete_portfolio_link(
    link_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await ProfileService(session).delete_portfolio_link(current_user.id, link_id)
    return ApiResponse(
        success=True, data={"deleted": True}, message="포트폴리오 링크가 삭제되었습니다."
    )
