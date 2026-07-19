from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.models.job import JobAnalysisStatus

Importance = Literal["LOW", "MEDIUM", "HIGH"]
QualificationImportance = Literal["REQUIRED", "PREFERRED", "UNKNOWN"]


class JobAnalysisPosition(BaseModel):
    title: str | None = None
    category: str | None = None
    seniority: str | None = None
    employment_type: str | None = None


class JobAnalysisResponsibility(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    importance: Importance = "MEDIUM"
    evidence: str | None = Field(default=None, max_length=1000)


class JobAnalysisQualification(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    category: str = Field(default="OTHER", max_length=80)
    importance: QualificationImportance = "UNKNOWN"
    evidence: str | None = Field(default=None, max_length=1000)


class JobAnalysisSkill(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(default="OTHER", max_length=80)
    requirement: QualificationImportance = "UNKNOWN"
    evidence: str | None = Field(default=None, max_length=1000)


class JobAnalysisExperience(BaseModel):
    minimum_years: int | None = Field(default=None, ge=0, le=80)
    maximum_years: int | None = Field(default=None, ge=0, le=80)
    entry_level_allowed: bool | None = None
    description: str | None = Field(default=None, max_length=1000)


class JobAnalysisEducation(BaseModel):
    minimum_level: str | None = Field(default=None, max_length=80)
    description: str | None = Field(default=None, max_length=1000)


class JobAnalysisWorkConditions(BaseModel):
    location: str | None = Field(default=None, max_length=200)
    work_type: str | None = Field(default=None, max_length=80)
    employment_type: str | None = Field(default=None, max_length=80)


class JobAnalysisDeadline(BaseModel):
    type: str | None = Field(default=None, max_length=80)
    date: datetime | None = None
    description: str | None = Field(default=None, max_length=1000)


class JobAnalysisCompanyValue(BaseModel):
    keyword: str = Field(min_length=1, max_length=120)
    evidence: str | None = Field(default=None, max_length=1000)


class JobAnalysisWarning(BaseModel):
    code: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=500)


class JobAnalysisConfidence(BaseModel):
    overall: float = Field(default=0.0, ge=0, le=1)
    responsibilities: float = Field(default=0.0, ge=0, le=1)
    qualifications: float = Field(default=0.0, ge=0, le=1)
    skills: float = Field(default=0.0, ge=0, le=1)
    deadline: float = Field(default=0.0, ge=0, le=1)


class JobAnalysisStructuredData(BaseModel):
    summary: str = Field(default="", max_length=3000)
    position: JobAnalysisPosition = Field(default_factory=JobAnalysisPosition)
    responsibilities: list[JobAnalysisResponsibility] = Field(default_factory=list)
    required_qualifications: list[JobAnalysisQualification] = Field(default_factory=list)
    preferred_qualifications: list[JobAnalysisQualification] = Field(default_factory=list)
    technical_skills: list[JobAnalysisSkill] = Field(default_factory=list)
    experience: JobAnalysisExperience = Field(default_factory=JobAnalysisExperience)
    education: JobAnalysisEducation = Field(default_factory=JobAnalysisEducation)
    work_conditions: JobAnalysisWorkConditions = Field(default_factory=JobAnalysisWorkConditions)
    recruitment_process: list[str] = Field(default_factory=list)
    deadline: JobAnalysisDeadline = Field(default_factory=JobAnalysisDeadline)
    company_values: list[JobAnalysisCompanyValue] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    warnings: list[JobAnalysisWarning] = Field(default_factory=list)
    confidence: JobAnalysisConfidence = Field(default_factory=JobAnalysisConfidence)

    @field_validator("recruitment_process", "keywords")
    @classmethod
    def strip_list_items(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


class JobAnalysisRunRequest(BaseModel):
    force: bool = False


class JobAnalysisUpdate(BaseModel):
    summary: str | None = Field(default=None, max_length=3000)
    position_data: dict[str, Any] | None = None
    responsibilities: list[dict[str, Any]] | None = None
    required_qualifications: list[dict[str, Any]] | None = None
    preferred_qualifications: list[dict[str, Any]] | None = None
    technical_skills: list[dict[str, Any]] | None = None
    experience_data: dict[str, Any] | None = None
    education_data: dict[str, Any] | None = None
    work_conditions: dict[str, Any] | None = None
    recruitment_process: list[str] | None = None
    deadline_data: dict[str, Any] | None = None
    company_values: list[dict[str, Any]] | None = None
    keywords: list[str] | None = None
    warnings: list[dict[str, Any]] | None = None
    confidence: dict[str, Any] | None = None


class JobAnalysisPublic(BaseModel):
    id: int
    job_posting_id: int
    user_id: int
    status: JobAnalysisStatus
    schema_version: str
    prompt_version: str
    input_hash: str
    input_length: int
    summary: str | None
    position_data: dict[str, Any] | None
    responsibilities: list[dict[str, Any]] | None
    required_qualifications: list[dict[str, Any]] | None
    preferred_qualifications: list[dict[str, Any]] | None
    technical_skills: list[dict[str, Any]] | None
    experience_data: dict[str, Any] | None
    education_data: dict[str, Any] | None
    work_conditions: dict[str, Any] | None
    recruitment_process: list[str] | None
    deadline_data: dict[str, Any] | None
    company_values: list[dict[str, Any]] | None
    keywords: list[str] | None
    warnings: list[dict[str, Any]] | None
    confidence: dict[str, Any] | None
    is_user_edited: bool
    is_outdated: bool
    analyzed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobAnalysisRunPublic(BaseModel):
    id: int
    job_posting_id: int
    job_analysis_id: int | None
    user_id: int
    status: JobAnalysisStatus
    provider: str
    model: str | None
    schema_version: str
    prompt_version: str
    input_hash: str
    input_length: int
    request_id: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    latency_ms: int | None
    error_code: str | None
    error_message: str | None
    raw_response: str | None
    started_at: datetime
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobAnalysisRunsData(BaseModel):
    items: list[JobAnalysisRunPublic]
    page: int
    size: int
    total: int
    total_pages: int


class AIProviderStatusData(BaseModel):
    active_provider: str
    enabled: bool
    model: str | None
    analysis_available: bool


class JobAnalysisDeletedData(BaseModel):
    deleted: bool
