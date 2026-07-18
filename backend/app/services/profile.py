from typing import Any

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.models.career import (
    CareerProfile,
    ExcludedCondition,
    Experience,
    JobPreference,
    PortfolioLink,
    Project,
    ProjectSkill,
    Skill,
    UserSkill,
)
from app.repositories.profile import ProfileRepository
from app.schemas.profile import (
    CareerProfileCreate,
    CareerProfileUpdate,
    ExcludedConditionCreate,
    ExcludedConditionUpdate,
    ExperienceCreate,
    ExperienceUpdate,
    JobPreferencePayload,
    PortfolioLinkCreate,
    PortfolioLinkUpdate,
    ProjectCreate,
    ProjectUpdate,
    SkillCategory,
    UserSkillCreate,
    UserSkillUpdate,
)


def normalize_skill_name(name: str) -> str:
    return " ".join(name.strip().lower().split())


def model_data(payload: Any, *, exclude_unset: bool = False) -> dict[str, Any]:
    return payload.model_dump(exclude_unset=exclude_unset)


class ProfileService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ProfileRepository(session)

    async def get_profile(self, user_id: int) -> CareerProfile:
        profile = await self.repository.get_profile(user_id)
        if not profile:
            raise AppError("PROFILE_NOT_FOUND", "커리어 프로필을 찾을 수 없습니다.", 404)
        return profile

    async def create_profile(self, user_id: int, payload: CareerProfileCreate) -> CareerProfile:
        if await self.repository.get_profile(user_id):
            raise AppError("PROFILE_ALREADY_EXISTS", "이미 커리어 프로필이 있습니다.", 409)
        profile = CareerProfile(user_id=user_id, **model_data(payload))
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def update_profile(self, user_id: int, payload: CareerProfileUpdate) -> CareerProfile:
        profile = await self.get_profile(user_id)
        for key, value in model_data(payload, exclude_unset=True).items():
            setattr(profile, key, value)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def get_or_create_skill(self, name: str, category: SkillCategory) -> Skill:
        normalized_name = normalize_skill_name(name)
        skill = await self.repository.get_skill_by_normalized_name(normalized_name)
        if skill:
            return skill
        skill = Skill(name=name.strip(), normalized_name=normalized_name, category=category)
        self.session.add(skill)
        await self.session.flush()
        await self.session.refresh(skill)
        return skill

    async def list_user_skills(self, user_id: int) -> list[UserSkill]:
        return await self.repository.list_user_skills(user_id)

    async def add_user_skill(self, user_id: int, payload: UserSkillCreate) -> UserSkill:
        skill = await self.get_or_create_skill(payload.name, payload.category)
        if await self.repository.get_user_skill_by_skill(user_id, skill.id):
            raise AppError("SKILL_ALREADY_REGISTERED", "이미 등록된 기술입니다.", 409)
        user_skill = UserSkill(
            user_id=user_id,
            skill_id=skill.id,
            proficiency_level=payload.proficiency_level,
            years_of_experience=payload.years_of_experience,
            is_primary=payload.is_primary,
        )
        self.session.add(user_skill)
        await self.session.commit()
        return await self.get_user_skill(user_id, user_skill.id)

    async def get_user_skill(self, user_id: int, user_skill_id: int) -> UserSkill:
        user_skill = await self.repository.get_user_skill(user_id, user_skill_id)
        if not user_skill:
            raise AppError("USER_SKILL_NOT_FOUND", "사용자 기술을 찾을 수 없습니다.", 404)
        return user_skill

    async def update_user_skill(
        self, user_id: int, user_skill_id: int, payload: UserSkillUpdate
    ) -> UserSkill:
        user_skill = await self.get_user_skill(user_id, user_skill_id)
        for key, value in model_data(payload, exclude_unset=True).items():
            setattr(user_skill, key, value)
        await self.session.commit()
        return await self.get_user_skill(user_id, user_skill_id)

    async def delete_user_skill(self, user_id: int, user_skill_id: int) -> None:
        user_skill = await self.get_user_skill(user_id, user_skill_id)
        await self.session.delete(user_skill)
        await self.session.commit()

    async def list_experiences(self, user_id: int) -> list[Experience]:
        return await self.repository.list_experiences(user_id)

    async def get_experience(self, user_id: int, experience_id: int) -> Experience:
        experience = await self.repository.get_experience(user_id, experience_id)
        if not experience:
            raise AppError("EXPERIENCE_NOT_FOUND", "경력을 찾을 수 없습니다.", 404)
        return experience

    async def create_experience(self, user_id: int, payload: ExperienceCreate) -> Experience:
        experience = Experience(user_id=user_id, **model_data(payload))
        self.session.add(experience)
        await self.session.commit()
        await self.session.refresh(experience)
        return experience

    async def update_experience(
        self, user_id: int, experience_id: int, payload: ExperienceUpdate
    ) -> Experience:
        experience = await self.get_experience(user_id, experience_id)
        for key, value in model_data(payload, exclude_unset=True).items():
            setattr(experience, key, value)
        self.validate_experience_dates(experience)
        await self.session.commit()
        await self.session.refresh(experience)
        return experience

    def validate_experience_dates(self, experience: Experience) -> None:
        if experience.end_date and experience.end_date < experience.start_date:
            raise AppError(
                "EXPERIENCE_INVALID_DATE_RANGE", "경력 종료일이 시작일보다 빠릅니다.", 422
            )
        if experience.is_current and experience.end_date is not None:
            raise AppError(
                "EXPERIENCE_INVALID_DATE_RANGE", "재직 중인 경력은 종료일을 비워야 합니다.", 422
            )
        if not experience.is_current and experience.end_date is None:
            raise AppError(
                "EXPERIENCE_INVALID_DATE_RANGE", "종료된 경력은 종료일이 필요합니다.", 422
            )

    async def delete_experience(self, user_id: int, experience_id: int) -> None:
        experience = await self.get_experience(user_id, experience_id)
        await self.session.delete(experience)
        await self.session.commit()

    async def list_projects(self, user_id: int) -> list[Project]:
        return await self.repository.list_projects(user_id)

    async def get_project(self, user_id: int, project_id: int) -> Project:
        project = await self.repository.get_project(user_id, project_id)
        if not project:
            raise AppError("PROJECT_NOT_FOUND", "프로젝트를 찾을 수 없습니다.", 404)
        return project

    async def create_project(self, user_id: int, payload: ProjectCreate) -> Project:
        data = model_data(payload)
        skill_names = data.pop("skill_names", [])
        project = Project(user_id=user_id, **data)
        self.session.add(project)
        await self.session.flush()
        await self.replace_project_skills(project, skill_names)
        await self.session.commit()
        return await self.get_project(user_id, project.id)

    async def update_project(
        self, user_id: int, project_id: int, payload: ProjectUpdate
    ) -> Project:
        project = await self.get_project(user_id, project_id)
        data = model_data(payload, exclude_unset=True)
        skill_names = data.pop("skill_names", None)
        for key, value in data.items():
            setattr(project, key, value)
        self.validate_project_dates(project)
        if skill_names is not None:
            await self.replace_project_skills(project, skill_names)
        await self.session.commit()
        return await self.get_project(user_id, project_id)

    def validate_project_dates(self, project: Project) -> None:
        if project.end_date and project.end_date < project.start_date:
            raise AppError(
                "PROJECT_INVALID_DATE_RANGE", "프로젝트 종료일이 시작일보다 빠릅니다.", 422
            )
        if project.is_ongoing and project.end_date is not None:
            raise AppError(
                "PROJECT_INVALID_DATE_RANGE", "진행 중인 프로젝트는 종료일을 비워야 합니다.", 422
            )

    async def replace_project_skills(self, project: Project, skill_names: list[str]) -> None:
        await self.session.execute(
            delete(ProjectSkill).where(ProjectSkill.project_id == project.id)
        )
        for name in dict.fromkeys(skill_names):
            skill = await self.get_or_create_skill(name, SkillCategory.ETC)
            self.session.add(ProjectSkill(project_id=project.id, skill_id=skill.id))
        self.session.expire(project, ["project_skills"])

    async def delete_project(self, user_id: int, project_id: int) -> None:
        project = await self.get_project(user_id, project_id)
        await self.session.delete(project)
        await self.session.commit()

    async def get_preferences(self, user_id: int) -> JobPreference:
        preferences = await self.repository.get_preferences(user_id)
        if not preferences:
            raise AppError("PREFERENCE_NOT_FOUND", "희망 조건을 찾을 수 없습니다.", 404)
        return preferences

    async def upsert_preferences(
        self, user_id: int, payload: JobPreferencePayload
    ) -> JobPreference:
        preferences = await self.repository.get_preferences(user_id)
        data = self.preference_data(payload)
        if preferences:
            for key, value in data.items():
                setattr(preferences, key, value)
        else:
            preferences = JobPreference(user_id=user_id, **data)
            self.session.add(preferences)
        await self.session.commit()
        await self.session.refresh(preferences)
        return preferences

    def preference_data(self, payload: JobPreferencePayload) -> dict[str, Any]:
        return {
            "preferred_employment_types": [
                item.value for item in payload.preferred_employment_types
            ],
            "preferred_locations": payload.preferred_locations,
            "preferred_company_sizes": [item.value for item in payload.preferred_company_sizes],
            "remote_preference": payload.remote_preference,
            "minimum_salary": payload.minimum_salary,
            "desired_roles": payload.desired_roles,
            "priority_keywords": payload.priority_keywords,
        }

    async def list_exclusions(self, user_id: int) -> list[ExcludedCondition]:
        return await self.repository.list_exclusions(user_id)

    async def create_exclusion(
        self, user_id: int, payload: ExcludedConditionCreate
    ) -> ExcludedCondition:
        for existing in await self.repository.list_exclusions(user_id):
            if (
                existing.condition_type == payload.condition_type
                and existing.value.lower() == payload.value.lower()
            ):
                raise AppError(
                    "VALIDATION_ERROR",
                    "이미 등록된 지원 제외 조건입니다.",
                    400,
                )
        condition = ExcludedCondition(user_id=user_id, **model_data(payload))
        self.session.add(condition)
        await self.session.commit()
        await self.session.refresh(condition)
        return condition

    async def update_exclusion(
        self, user_id: int, condition_id: int, payload: ExcludedConditionUpdate
    ) -> ExcludedCondition:
        condition = await self.get_exclusion(user_id, condition_id)
        data = model_data(payload, exclude_unset=True)
        next_type = data.get("condition_type", condition.condition_type)
        next_value = data.get("value", condition.value)
        for existing in await self.repository.list_exclusions(user_id):
            if (
                existing.id != condition.id
                and existing.condition_type == next_type
                and existing.value.lower() == next_value.lower()
            ):
                raise AppError(
                    "VALIDATION_ERROR",
                    "이미 등록된 지원 제외 조건입니다.",
                    400,
                )
        for key, value in data.items():
            setattr(condition, key, value)
        await self.session.commit()
        await self.session.refresh(condition)
        return condition

    async def get_exclusion(self, user_id: int, condition_id: int) -> ExcludedCondition:
        condition = await self.repository.get_exclusion(user_id, condition_id)
        if not condition:
            raise AppError("EXCLUDED_CONDITION_NOT_FOUND", "제외 조건을 찾을 수 없습니다.", 404)
        return condition

    async def delete_exclusion(self, user_id: int, condition_id: int) -> None:
        condition = await self.get_exclusion(user_id, condition_id)
        await self.session.delete(condition)
        await self.session.commit()

    async def list_portfolio_links(self, user_id: int) -> list[PortfolioLink]:
        return await self.repository.list_portfolio_links(user_id)

    async def create_portfolio_link(
        self, user_id: int, payload: PortfolioLinkCreate
    ) -> PortfolioLink:
        await self.ensure_portfolio_url_unique(user_id, payload.url)
        if payload.is_primary:
            await self.clear_primary_portfolio_links(user_id)
        link = PortfolioLink(user_id=user_id, **model_data(payload))
        self.session.add(link)
        await self.session.commit()
        await self.session.refresh(link)
        return link

    async def update_portfolio_link(
        self, user_id: int, link_id: int, payload: PortfolioLinkUpdate
    ) -> PortfolioLink:
        link = await self.get_portfolio_link(user_id, link_id)
        data = model_data(payload, exclude_unset=True)
        if "url" in data:
            await self.ensure_portfolio_url_unique(user_id, data["url"], exclude_link_id=link.id)
        if data.get("is_primary"):
            await self.clear_primary_portfolio_links(user_id)
        for key, value in data.items():
            setattr(link, key, value)
        await self.session.commit()
        await self.session.refresh(link)
        return link

    async def clear_primary_portfolio_links(self, user_id: int) -> None:
        for link in await self.repository.list_portfolio_links(user_id):
            link.is_primary = False

    async def ensure_portfolio_url_unique(
        self, user_id: int, url: str, exclude_link_id: int | None = None
    ) -> None:
        for link in await self.repository.list_portfolio_links(user_id):
            if link.id != exclude_link_id and link.url.lower() == url.lower():
                raise AppError(
                    "VALIDATION_ERROR",
                    "이미 등록된 포트폴리오 링크입니다.",
                    400,
                )

    async def get_portfolio_link(self, user_id: int, link_id: int) -> PortfolioLink:
        link = await self.repository.get_portfolio_link(user_id, link_id)
        if not link:
            raise AppError("PORTFOLIO_LINK_NOT_FOUND", "포트폴리오 링크를 찾을 수 없습니다.", 404)
        return link

    async def delete_portfolio_link(self, user_id: int, link_id: int) -> None:
        link = await self.get_portfolio_link(user_id, link_id)
        await self.session.delete(link)
        await self.session.commit()
