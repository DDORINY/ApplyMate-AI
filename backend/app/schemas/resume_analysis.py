from typing import Literal

from pydantic import BaseModel, Field, field_validator

ResumeEvidenceSource = Literal["RAW_TEXT", "EDITED_TEXT", "SECTION_CANDIDATE", "USER_PROFILE"]
ResumeAnalysisWarningCode = Literal[
    "MOCK_PROVIDER",
    "INSUFFICIENT_TEXT",
    "LOW_CONFIDENCE",
    "USER_REVIEW_REQUIRED",
]


class ResumeAnalysisEvidence(BaseModel):
    source: ResumeEvidenceSource
    text: str = Field(min_length=1, max_length=1000)
    page: int | None = Field(default=None, ge=1)


class ResumeAnalysisSkill(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(default="UNKNOWN", max_length=80)
    evidence: list[ResumeAnalysisEvidence] = Field(default_factory=list)


class ResumeAnalysisExperience(BaseModel):
    organization: str | None = Field(default=None, max_length=160)
    role: str | None = Field(default=None, max_length=160)
    period: str | None = Field(default=None, max_length=120)
    summary: str = Field(default="", max_length=1000)
    evidence: list[ResumeAnalysisEvidence] = Field(default_factory=list)


class ResumeAnalysisProject(BaseModel):
    name: str | None = Field(default=None, max_length=160)
    role: str | None = Field(default=None, max_length=160)
    summary: str = Field(default="", max_length=1000)
    skills: list[str] = Field(default_factory=list)
    evidence: list[ResumeAnalysisEvidence] = Field(default_factory=list)

    @field_validator("skills")
    @classmethod
    def strip_skills(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


class ResumeAnalysisEducation(BaseModel):
    school: str | None = Field(default=None, max_length=160)
    major: str | None = Field(default=None, max_length=160)
    degree: str | None = Field(default=None, max_length=120)
    period: str | None = Field(default=None, max_length=120)
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
    keywords: list[str] = Field(default_factory=list)
    warnings: list[ResumeAnalysisWarning] = Field(default_factory=list)
    confidence: ResumeAnalysisConfidence = Field(default_factory=ResumeAnalysisConfidence)

    @field_validator("keywords")
    @classmethod
    def strip_keywords(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]
