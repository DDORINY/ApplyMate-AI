from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.resume import ResumeAnalysisStatus

ResumeAnalysisInputSource = Literal["RAW", "EDITED"]
ResumeEvidenceSource = Literal["RAW_TEXT", "EDITED_TEXT", "SECTION_CANDIDATE", "USER_PROFILE"]
ResumeAnalysisWarningCode = Literal[
    "MOCK_PROVIDER",
    "INSUFFICIENT_TEXT",
    "LOW_CONFIDENCE",
    "USER_REVIEW_REQUIRED",
]


class ResumeAnalysisEvidence(BaseModel):
    source: ResumeEvidenceSource
    source_text: str = Field(min_length=1, max_length=1000)
    start_offset: int | None = Field(default=None, ge=0)
    end_offset: int | None = Field(default=None, ge=0)
    page_number: int | None = Field(default=None, ge=1)
    section_candidate: str | None = Field(default=None, max_length=80)
    extraction_id: int | None = Field(default=None, ge=1)


class ResumeAnalysisSkill(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(default="UNKNOWN", max_length=80)
    proficiency_candidate: str | None = Field(default=None, max_length=80)
    years_candidate: float | None = Field(default=None, ge=0, le=80)
    evidence: list[ResumeAnalysisEvidence] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0, le=1)


class ResumeAnalysisExperience(BaseModel):
    company: str | None = Field(default=None, max_length=160)
    position: str | None = Field(default=None, max_length=160)
    employment_type: str | None = Field(default=None, max_length=80)
    start_date: str | None = Field(default=None, max_length=40)
    end_date: str | None = Field(default=None, max_length=40)
    is_current: bool | None = None
    responsibilities: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    evidence: list[ResumeAnalysisEvidence] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0, le=1)


class ResumeAnalysisProject(BaseModel):
    name: str | None = Field(default=None, max_length=160)
    summary: str = Field(default="", max_length=1000)
    role: str | None = Field(default=None, max_length=160)
    period: str | None = Field(default=None, max_length=120)
    team_size: int | None = Field(default=None, ge=1, le=1000)
    technologies: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)
    evidence: list[ResumeAnalysisEvidence] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0, le=1)

    @field_validator("technologies", "responsibilities", "achievements", "links")
    @classmethod
    def strip_project_lists(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


class ResumeAnalysisEducation(BaseModel):
    institution: str | None = Field(default=None, max_length=160)
    major: str | None = Field(default=None, max_length=160)
    degree: str | None = Field(default=None, max_length=120)
    start_date: str | None = Field(default=None, max_length=40)
    end_date: str | None = Field(default=None, max_length=40)
    status: str | None = Field(default=None, max_length=80)
    evidence: list[ResumeAnalysisEvidence] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0, le=1)


class ResumeAnalysisCertification(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    issuer: str | None = Field(default=None, max_length=160)
    issued_date: str | None = Field(default=None, max_length=40)
    expiration_date: str | None = Field(default=None, max_length=40)
    credential_id: str | None = Field(default=None, max_length=120)
    evidence: list[ResumeAnalysisEvidence] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0, le=1)


class ResumeAnalysisAchievement(BaseModel):
    statement: str = Field(min_length=1, max_length=1000)
    metric: str | None = Field(default=None, max_length=160)
    context: str | None = Field(default=None, max_length=300)
    evidence: list[ResumeAnalysisEvidence] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0, le=1)


class ResumeAnalysisContact(BaseModel):
    email: str | None = Field(default=None, max_length=160)
    phone: str | None = Field(default=None, max_length=80)
    location: str | None = Field(default=None, max_length=160)
    links: list[str] = Field(default_factory=list)
    evidence: list[ResumeAnalysisEvidence] = Field(default_factory=list)


class ResumeAnalysisWarning(BaseModel):
    code: ResumeAnalysisWarningCode
    message: str = Field(min_length=1, max_length=500)


class ResumeAnalysisConfidence(BaseModel):
    overall: float = Field(default=0.0, ge=0, le=1)
    skills: float = Field(default=0.0, ge=0, le=1)
    experiences: float = Field(default=0.0, ge=0, le=1)
    projects: float = Field(default=0.0, ge=0, le=1)
    education: float = Field(default=0.0, ge=0, le=1)


class ResumeAnalysisStructuredData(BaseModel):
    summary: str = Field(default="", max_length=3000)
    headline: str | None = Field(default=None, max_length=200)
    skills: list[ResumeAnalysisSkill] = Field(default_factory=list)
    experiences: list[ResumeAnalysisExperience] = Field(default_factory=list)
    projects: list[ResumeAnalysisProject] = Field(default_factory=list)
    education: list[ResumeAnalysisEducation] = Field(default_factory=list)
    certifications: list[ResumeAnalysisCertification] = Field(default_factory=list)
    achievements: list[ResumeAnalysisAchievement] = Field(default_factory=list)
    awards: list[ResumeAnalysisAchievement] = Field(default_factory=list)
    portfolio_links: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    contact: ResumeAnalysisContact = Field(default_factory=ResumeAnalysisContact)
    other_sections: list[dict[str, Any]] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    warnings: list[ResumeAnalysisWarning] = Field(default_factory=list)
    confidence: ResumeAnalysisConfidence = Field(default_factory=ResumeAnalysisConfidence)

    @field_validator("keywords", "portfolio_links", "languages")
    @classmethod
    def strip_keywords(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


class ResumeAnalysisRunRequest(BaseModel):
    force: bool = False


class ResumeAnalysisUpdate(BaseModel):
    edited_result: dict[str, Any] = Field(default_factory=dict)


class ResumeAnalysisDeletedData(BaseModel):
    deleted: bool


class ResumeProfileCandidate(BaseModel):
    target: str = Field(min_length=1, max_length=80)
    action: Literal["ADD", "UPDATE", "DUPLICATE", "CONFLICT"]
    current_value: Any = None
    resume_value: Any = None
    difference: str | None = Field(default=None, max_length=500)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0, le=1)


class ResumeProfileCandidateData(BaseModel):
    items: list[ResumeProfileCandidate]


class ResumeAnalysisRunPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    analysis_id: int | None
    resume_id: int
    resume_file_id: int
    extraction_id: int
    user_id: int
    status: ResumeAnalysisStatus
    provider: str
    model: str | None
    prompt_version: str
    schema_version: str
    input_hash: str
    input_source: str
    input_length: int
    started_at: datetime
    completed_at: datetime | None
    error_code: str | None
    error_message: str | None
    result_snapshot: dict[str, Any] | None
    usage_metadata: dict[str, Any]
    raw_response_metadata: dict[str, Any]
    created_at: datetime


class ResumeAnalysisRunsData(BaseModel):
    items: list[ResumeAnalysisRunPublic]
    page: int
    size: int
    total: int
    total_pages: int


class ResumeAnalysisPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    resume_file_id: int
    extraction_id: int
    user_id: int
    status: ResumeAnalysisStatus
    provider: str | None
    model: str | None
    prompt_version: str
    schema_version: str
    input_hash: str
    resume_file_hash: str
    extraction_run_id: int | None
    input_source: str
    input_length: int
    summary: str | None
    structured_result: dict[str, Any] | None
    edited_result: dict[str, Any] | None
    result: dict[str, Any] | None
    profile_candidates: list[dict[str, Any]]
    is_user_edited: bool
    is_outdated: bool
    latest_run_id: int | None
    error_code: str | None
    error_message: str | None
    analyzed_at: datetime | None
    created_at: datetime
    updated_at: datetime
