from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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


class ProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_profile(self, user_id: int) -> CareerProfile | None:
        result = await self.session.execute(
            select(CareerProfile).where(CareerProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_skill_by_normalized_name(self, normalized_name: str) -> Skill | None:
        result = await self.session.execute(
            select(Skill).where(Skill.normalized_name == normalized_name)
        )
        return result.scalar_one_or_none()

    async def list_user_skills(self, user_id: int) -> list[UserSkill]:
        result = await self.session.execute(
            select(UserSkill)
            .options(selectinload(UserSkill.skill))
            .where(UserSkill.user_id == user_id)
            .order_by(UserSkill.is_primary.desc(), UserSkill.id)
        )
        return list(result.scalars())

    async def get_user_skill(self, user_id: int, user_skill_id: int) -> UserSkill | None:
        result = await self.session.execute(
            select(UserSkill)
            .options(selectinload(UserSkill.skill))
            .where(UserSkill.id == user_skill_id, UserSkill.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_skill_by_skill(self, user_id: int, skill_id: int) -> UserSkill | None:
        result = await self.session.execute(
            select(UserSkill).where(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
        )
        return result.scalar_one_or_none()

    async def list_experiences(self, user_id: int) -> list[Experience]:
        result = await self.session.execute(
            select(Experience)
            .where(Experience.user_id == user_id)
            .order_by(Experience.start_date.desc())
        )
        return list(result.scalars())

    async def get_experience(self, user_id: int, experience_id: int) -> Experience | None:
        result = await self.session.execute(
            select(Experience).where(Experience.id == experience_id, Experience.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_projects(self, user_id: int) -> list[Project]:
        result = await self.session.execute(
            select(Project)
            .options(selectinload(Project.project_skills).selectinload(ProjectSkill.skill))
            .where(Project.user_id == user_id)
            .order_by(Project.start_date.desc(), Project.id.desc())
        )
        return list(result.scalars())

    async def get_project(self, user_id: int, project_id: int) -> Project | None:
        result = await self.session.execute(
            select(Project)
            .options(selectinload(Project.project_skills).selectinload(ProjectSkill.skill))
            .where(Project.id == project_id, Project.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_preferences(self, user_id: int) -> JobPreference | None:
        result = await self.session.execute(
            select(JobPreference).where(JobPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_exclusions(self, user_id: int) -> list[ExcludedCondition]:
        result = await self.session.execute(
            select(ExcludedCondition)
            .where(ExcludedCondition.user_id == user_id)
            .order_by(ExcludedCondition.id.desc())
        )
        return list(result.scalars())

    async def get_exclusion(self, user_id: int, condition_id: int) -> ExcludedCondition | None:
        result = await self.session.execute(
            select(ExcludedCondition).where(
                ExcludedCondition.id == condition_id, ExcludedCondition.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_portfolio_links(self, user_id: int) -> list[PortfolioLink]:
        result = await self.session.execute(
            select(PortfolioLink)
            .where(PortfolioLink.user_id == user_id)
            .order_by(PortfolioLink.display_order, PortfolioLink.id)
        )
        return list(result.scalars())

    async def get_portfolio_link(self, user_id: int, link_id: int) -> PortfolioLink | None:
        result = await self.session.execute(
            select(PortfolioLink).where(
                PortfolioLink.id == link_id, PortfolioLink.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
