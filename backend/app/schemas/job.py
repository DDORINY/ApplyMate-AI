from datetime import datetime
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.job import (
    CompanySize,
    JobDeadlineType,
    JobEmploymentType,
    JobPostingStatus,
    JobSourceType,
    JobWorkType,
)


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = " ".join(value.strip().split()) if len(value) <= 500 else value.strip()
    return stripped or None


def validate_http_url(value: str | None) -> str | None:
    value = clean_text(value)
    if value is None:
        return None
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("http 또는 https URL만 사용할 수 있습니다.")
    if parsed.username or parsed.password:
        raise ValueError("인증정보가 포함된 URL은 사용할 수 없습니다.")
    return value


class CompanyPayload(BaseModel):
    company_name: str = Field(min_length=1, max_length=160)
    company_website_url: str | None = Field(default=None, max_length=500)
    company_size: CompanySize = CompanySize.UNKNOWN
    company_industry: str | None = Field(default=None, max_length=120)
    company_description: str | None = Field(default=None, max_length=3000)

    @field_validator("company_name", "company_industry", "company_description")
    @classmethod
    def trim_company_text(cls, value: str | None) -> str | None:
        return clean_text(value)

    @field_validator("company_website_url")
    @classmethod
    def validate_company_url(cls, value: str | None) -> str | None:
        return validate_http_url(value)


class JobPostingBase(CompanyPayload):
    title: str = Field(min_length=1, max_length=200)
    position: str | None = Field(default=None, max_length=160)
    employment_type: JobEmploymentType = JobEmploymentType.UNKNOWN
    career_requirement: str | None = Field(default=None, max_length=300)
    education_requirement: str | None = Field(default=None, max_length=300)
    location: str | None = Field(default=None, max_length=200)
    work_type: JobWorkType = JobWorkType.UNKNOWN
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    salary_text: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=20000)
    requirements: str | None = Field(default=None, max_length=20000)
    preferred_qualifications: str | None = Field(default=None, max_length=20000)
    benefits: str | None = Field(default=None, max_length=10000)
    recruitment_process: str | None = Field(default=None, max_length=10000)
    source_type: JobSourceType = JobSourceType.MANUAL
    source_url: str | None = Field(default=None, max_length=1000)
    original_content: str | None = Field(default=None, max_length=20000)
    published_at: datetime | None = None
    deadline_at: datetime | None = None
    deadline_type: JobDeadlineType = JobDeadlineType.UNKNOWN
    status: JobPostingStatus = JobPostingStatus.SAVED
    is_favorite: bool = False
    notes: str | None = Field(default=None, max_length=5000)
    collected_at: datetime | None = None

    @field_validator(
        "title",
        "position",
        "career_requirement",
        "education_requirement",
        "location",
        "salary_text",
        "description",
        "requirements",
        "preferred_qualifications",
        "benefits",
        "recruitment_process",
        "original_content",
        "notes",
    )
    @classmethod
    def trim_text_fields(cls, value: str | None) -> str | None:
        return clean_text(value)

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, value: str | None) -> str | None:
        return validate_http_url(value)

    @model_validator(mode="after")
    def validate_ranges(self):
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("최소 급여는 최대 급여보다 클 수 없습니다.")
        if self.published_at and self.deadline_at and self.deadline_at < self.published_at:
            raise ValueError("마감일은 게시일보다 빠를 수 없습니다.")
        if self.deadline_type == JobDeadlineType.FIXED and self.deadline_at is None:
            raise ValueError("고정 마감일은 deadline_at이 필요합니다.")
        if self.source_type == JobSourceType.MANUAL and self.source_url is None:
            return self
        if self.source_type == JobSourceType.URL and self.source_url is None:
            raise ValueError("URL 등록은 source_url이 필요합니다.")
        return self


class JobPostingCreate(JobPostingBase):
    pass


class JobPostingUrlImportRequest(BaseModel):
    url: str = Field(min_length=1, max_length=1000)
    company_name: str | None = Field(default=None, max_length=160)
    title: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=20000)
    status: JobPostingStatus = JobPostingStatus.SAVED
    is_favorite: bool = False
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        return validate_http_url(value) or value

    @field_validator("company_name", "title", "description", "notes")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        return clean_text(value)


class JobPostingUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=160)
    company_website_url: str | None = Field(default=None, max_length=500)
    company_size: CompanySize | None = None
    company_industry: str | None = Field(default=None, max_length=120)
    company_description: str | None = Field(default=None, max_length=3000)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    position: str | None = Field(default=None, max_length=160)
    employment_type: JobEmploymentType | None = None
    career_requirement: str | None = Field(default=None, max_length=300)
    education_requirement: str | None = Field(default=None, max_length=300)
    location: str | None = Field(default=None, max_length=200)
    work_type: JobWorkType | None = None
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    salary_text: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=20000)
    requirements: str | None = Field(default=None, max_length=20000)
    preferred_qualifications: str | None = Field(default=None, max_length=20000)
    benefits: str | None = Field(default=None, max_length=10000)
    recruitment_process: str | None = Field(default=None, max_length=10000)
    source_url: str | None = Field(default=None, max_length=1000)
    published_at: datetime | None = None
    deadline_at: datetime | None = None
    deadline_type: JobDeadlineType | None = None
    status: JobPostingStatus | None = None
    is_favorite: bool | None = None
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("company_website_url", "source_url")
    @classmethod
    def validate_url_fields(cls, value: str | None) -> str | None:
        return validate_http_url(value)


class CompanyPublic(BaseModel):
    id: int
    name: str
    normalized_name: str
    website_url: str | None
    industry: str | None
    company_size: CompanySize
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobPostingPublic(BaseModel):
    id: int
    user_id: int
    company_id: int
    company: CompanyPublic
    title: str
    position: str | None
    employment_type: JobEmploymentType
    career_requirement: str | None
    education_requirement: str | None
    location: str | None
    work_type: JobWorkType
    salary_min: int | None
    salary_max: int | None
    salary_text: str | None
    description: str | None
    requirements: str | None
    preferred_qualifications: str | None
    benefits: str | None
    recruitment_process: str | None
    source_type: JobSourceType
    source_url: str | None
    source_site: str | None
    original_content: str | None
    published_at: datetime | None
    deadline_at: datetime | None
    deadline_type: JobDeadlineType
    status: JobPostingStatus
    is_favorite: bool
    notes: str | None
    collected_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobPostingListData(BaseModel):
    items: list[JobPostingPublic]
    page: int
    size: int
    total: int
    total_pages: int


class JobPostingImportData(BaseModel):
    job: JobPostingPublic
    import_status: Literal["SUCCESS", "PARTIAL"]
    extracted_fields: list[str]
    warnings: list[str]


class JobPostingDeletedData(BaseModel):
    deleted: bool
