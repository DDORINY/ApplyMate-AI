from datetime import date, datetime
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.career import (
    CareerLevel,
    CompanySize,
    EmploymentType,
    ExcludedConditionType,
    PortfolioLinkType,
    ProficiencyLevel,
    RemotePreference,
    SkillCategory,
)


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def clean_list(values: list[str]) -> list[str]:
    return [item.strip() for item in values if item.strip()]


def validate_http_url(value: str | None) -> str | None:
    value = clean_text(value)
    if value is None:
        return None
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("http 또는 https URL만 사용할 수 있습니다.")
    return value


class CareerProfileBase(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)
    headline: str | None = Field(default=None, max_length=160)
    career_level: CareerLevel
    years_of_experience: int = Field(ge=0, le=60)
    desired_job_title: str = Field(min_length=1, max_length=100)
    introduction: str | None = Field(default=None, max_length=2000)

    @field_validator("display_name", "headline", "desired_job_title", "introduction")
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        return clean_text(value)


class CareerProfileCreate(CareerProfileBase):
    pass


class CareerProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=100)
    headline: str | None = Field(default=None, max_length=160)
    career_level: CareerLevel | None = None
    years_of_experience: int | None = Field(default=None, ge=0, le=60)
    desired_job_title: str | None = Field(default=None, min_length=1, max_length=100)
    introduction: str | None = Field(default=None, max_length=2000)

    @field_validator("display_name", "headline", "desired_job_title", "introduction")
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        return clean_text(value)


class CareerProfilePublic(CareerProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserSkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    category: SkillCategory = SkillCategory.ETC
    proficiency_level: ProficiencyLevel
    years_of_experience: int = Field(default=0, ge=0, le=60)
    is_primary: bool = False

    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        return value.strip()


class UserSkillUpdate(BaseModel):
    proficiency_level: ProficiencyLevel | None = None
    years_of_experience: int | None = Field(default=None, ge=0, le=60)
    is_primary: bool | None = None


class SkillPublic(BaseModel):
    id: int
    name: str
    normalized_name: str
    category: SkillCategory

    model_config = {"from_attributes": True}


class UserSkillPublic(BaseModel):
    id: int
    proficiency_level: ProficiencyLevel
    years_of_experience: int
    is_primary: bool
    skill: SkillPublic
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DateRangeMixin(BaseModel):
    start_date: date
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_range(self) -> Any:
        end_date = getattr(self, "end_date", None)
        if end_date and end_date < self.start_date:
            raise ValueError("종료일은 시작일보다 빠를 수 없습니다.")
        return self


class ExperienceBase(DateRangeMixin):
    company_name: str = Field(min_length=1, max_length=120)
    position: str = Field(min_length=1, max_length=120)
    employment_type: EmploymentType
    is_current: bool = False
    description: str | None = Field(default=None, max_length=3000)
    achievements: str | None = Field(default=None, max_length=3000)

    @field_validator("company_name", "position", "description", "achievements")
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        return clean_text(value)

    @model_validator(mode="after")
    def validate_current_job(self) -> Any:
        if self.is_current and self.end_date is not None:
            raise ValueError("재직 중인 경력은 종료일을 입력하지 않습니다.")
        if not self.is_current and self.end_date is None:
            raise ValueError("재직 중이 아닌 경력은 종료일이 필요합니다.")
        return self


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=120)
    position: str | None = Field(default=None, min_length=1, max_length=120)
    employment_type: EmploymentType | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None
    description: str | None = Field(default=None, max_length=3000)
    achievements: str | None = Field(default=None, max_length=3000)

    @field_validator("company_name", "position", "description", "achievements")
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        return clean_text(value)


class ExperiencePublic(ExperienceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectBase(DateRangeMixin):
    name: str = Field(min_length=1, max_length=120)
    summary: str | None = Field(default=None, max_length=300)
    role: str | None = Field(default=None, max_length=120)
    is_ongoing: bool = False
    description: str | None = Field(default=None, max_length=4000)
    responsibilities: str | None = Field(default=None, max_length=4000)
    achievements: str | None = Field(default=None, max_length=4000)
    repository_url: str | None = Field(default=None, max_length=500)
    service_url: str | None = Field(default=None, max_length=500)
    skill_names: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("name", "summary", "role", "description", "responsibilities", "achievements")
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        return clean_text(value)

    @field_validator("repository_url", "service_url")
    @classmethod
    def validate_url(cls, value: str | None) -> str | None:
        return validate_http_url(value)

    @field_validator("skill_names")
    @classmethod
    def trim_skills(cls, value: list[str]) -> list[str]:
        return clean_list(value)

    @model_validator(mode="after")
    def validate_ongoing_project(self) -> Any:
        if self.is_ongoing and self.end_date is not None:
            raise ValueError("진행 중인 프로젝트는 종료일을 입력하지 않습니다.")
        return self


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    summary: str | None = Field(default=None, max_length=300)
    role: str | None = Field(default=None, max_length=120)
    start_date: date | None = None
    end_date: date | None = None
    is_ongoing: bool | None = None
    description: str | None = Field(default=None, max_length=4000)
    responsibilities: str | None = Field(default=None, max_length=4000)
    achievements: str | None = Field(default=None, max_length=4000)
    repository_url: str | None = Field(default=None, max_length=500)
    service_url: str | None = Field(default=None, max_length=500)
    skill_names: list[str] | None = None

    @field_validator("repository_url", "service_url")
    @classmethod
    def validate_url(cls, value: str | None) -> str | None:
        return validate_http_url(value)


class ProjectPublic(BaseModel):
    id: int
    user_id: int
    name: str
    summary: str | None
    role: str | None
    start_date: date
    end_date: date | None
    is_ongoing: bool
    description: str | None
    responsibilities: str | None
    achievements: str | None
    repository_url: str | None
    service_url: str | None
    skills: list[SkillPublic] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobPreferencePayload(BaseModel):
    preferred_employment_types: list[EmploymentType] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    preferred_company_sizes: list[CompanySize] = Field(default_factory=list)
    remote_preference: RemotePreference = RemotePreference.ANY
    minimum_salary: int | None = Field(default=None, ge=0)
    desired_roles: list[str] = Field(default_factory=list)
    priority_keywords: list[str] = Field(default_factory=list)

    @field_validator("preferred_locations", "desired_roles", "priority_keywords")
    @classmethod
    def trim_list(cls, value: list[str]) -> list[str]:
        return clean_list(value)


class JobPreferencePublic(JobPreferencePayload):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExcludedConditionCreate(BaseModel):
    condition_type: ExcludedConditionType
    value: str = Field(min_length=1, max_length=160)
    reason: str | None = Field(default=None, max_length=300)
    is_active: bool = True

    @field_validator("value", "reason")
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        return clean_text(value)


class ExcludedConditionUpdate(BaseModel):
    condition_type: ExcludedConditionType | None = None
    value: str | None = Field(default=None, min_length=1, max_length=160)
    reason: str | None = Field(default=None, max_length=300)
    is_active: bool | None = None


class ExcludedConditionPublic(ExcludedConditionCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PortfolioLinkCreate(BaseModel):
    link_type: PortfolioLinkType
    title: str = Field(min_length=1, max_length=120)
    url: str = Field(min_length=1, max_length=500)
    is_primary: bool = False
    display_order: int = Field(default=0, ge=0)

    @field_validator("title")
    @classmethod
    def trim_title(cls, value: str) -> str:
        return value.strip()

    @field_validator("url")
    @classmethod
    def validate_portfolio_url(cls, value: str) -> str:
        return validate_http_url(value) or value


class PortfolioLinkUpdate(BaseModel):
    link_type: PortfolioLinkType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=120)
    url: str | None = Field(default=None, min_length=1, max_length=500)
    is_primary: bool | None = None
    display_order: int | None = Field(default=None, ge=0)

    @field_validator("url")
    @classmethod
    def validate_portfolio_url(cls, value: str | None) -> str | None:
        return validate_http_url(value)


class PortfolioLinkPublic(PortfolioLinkCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
