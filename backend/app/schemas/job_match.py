from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.job import (
    JobMatchFeedbackType,
    JobMatchGrade,
    JobMatchRecommendationStatus,
    JobMatchStatus,
)


class JobMatchRunRequest(BaseModel):
    force: bool = False
    generate_explanation: bool = True


class JobMatchScores(BaseModel):
    role: int = Field(ge=0, le=100)
    skill: int = Field(ge=0, le=100)
    experience: int = Field(ge=0, le=100)
    project: int = Field(ge=0, le=100)
    preference: int = Field(ge=0, le=100)
    risk: int = Field(ge=0, le=100)


class JobMatchPublic(BaseModel):
    id: int
    user_id: int
    job_posting_id: int
    job_analysis_id: int
    status: JobMatchStatus
    total_score: int
    grade: JobMatchGrade
    recommendation_status: JobMatchRecommendationStatus
    scores: JobMatchScores
    matched_skills: list[dict[str, Any]]
    missing_skills: list[dict[str, Any]]
    matched_projects: list[dict[str, Any]]
    strengths: list[dict[str, Any]]
    gaps: list[dict[str, Any]]
    risks: list[dict[str, Any]]
    recommendation_summary: str | None
    profile_completeness: int
    profile_hash: str
    job_analysis_hash: str
    calculation_version: str
    explanation_provider: str
    is_outdated: bool
    calculated_at: datetime | None
    created_at: datetime
    updated_at: datetime


class JobMatchRunPublic(BaseModel):
    id: int
    job_match_id: int | None
    user_id: int
    job_posting_id: int
    job_analysis_id: int
    status: JobMatchStatus
    profile_hash: str
    job_analysis_hash: str
    calculation_version: str
    total_score: int | None
    result_snapshot: dict[str, Any] | None
    error_code: str | None
    error_message: str | None
    started_at: datetime
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobMatchRunsData(BaseModel):
    items: list[JobMatchRunPublic]
    page: int
    size: int
    total: int
    total_pages: int


class JobMatchDeletedData(BaseModel):
    deleted: bool


class JobMatchFeedbackCreate(BaseModel):
    feedback_type: JobMatchFeedbackType
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


class JobMatchFeedbackUpdate(BaseModel):
    feedback_type: JobMatchFeedbackType | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


class JobMatchFeedbackPublic(BaseModel):
    id: int
    job_match_id: int
    user_id: int
    feedback_type: JobMatchFeedbackType
    rating: int | None
    comment: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobMatchFeedbackListData(BaseModel):
    items: list[JobMatchFeedbackPublic]
