from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models.job_recommendation import (
    JobRecommendationFeedbackReason,
    JobRecommendationFeedbackType,
    JobRecommendationGrade,
    JobRecommendationMatchStatus,
    JobRecommendationReasonType,
    JobRecommendationRequirementType,
    JobRecommendationRunStatus,
    JobRecommendationSeverity,
    JobRecommendationStatus,
    JobRecommendationType,
)


class JobRecommendationGenerateRequest(BaseModel):
    force_refresh: bool = False
    include_jobs_without_analysis: bool = True
    exclude_applied_jobs: bool = True
    max_jobs: int = Field(default=200, ge=1, le=500)


class JobRecommendationRunPublic(BaseModel):
    id: int
    user_id: int
    status: JobRecommendationRunStatus
    policy_version: str
    input_job_count: int
    recommended_count: int
    excluded_count: int
    failed_count: int
    started_at: datetime
    completed_at: datetime | None
    error_code: str | None
    safe_error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobRecommendationGenerateData(BaseModel):
    run_id: int
    status: JobRecommendationRunStatus
    policy_version: str
    input_job_count: int
    recommended_count: int
    excluded_count: int
    failed_count: int


class JobRecommendationReasonPublic(BaseModel):
    id: int
    reason_type: JobRecommendationReasonType
    requirement_type: JobRecommendationRequirementType
    label: str
    normalized_value: str | None
    match_status: JobRecommendationMatchStatus
    weight: int
    score_delta: int
    severity: JobRecommendationSeverity
    evidence: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobRecommendationFeedbackCreate(BaseModel):
    feedback_type: JobRecommendationFeedbackType
    reason_code: JobRecommendationFeedbackReason | None = None
    comment: str | None = Field(default=None, max_length=1000)


class JobRecommendationFeedbackPublic(BaseModel):
    id: int
    user_id: int
    recommendation_id: int
    feedback_type: JobRecommendationFeedbackType
    reason_code: JobRecommendationFeedbackReason | None
    comment: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobRecommendationJobSummary(BaseModel):
    id: int
    title: str
    position: str | None
    company_name: str
    employment_type: str
    location: str | None
    deadline_at: datetime | None
    status: str


class JobRecommendationPublic(BaseModel):
    id: int
    user_id: int
    job_id: int
    run_id: int
    score: int
    grade: JobRecommendationGrade
    recommendation_type: JobRecommendationType
    has_blocking_mismatch: bool
    matched_count: int
    missing_count: int
    unknown_count: int
    policy_version: str
    score_breakdown: dict[str, int] = Field(default_factory=dict)
    input_snapshot: dict[str, Any] = Field(default_factory=dict)
    missing_profile_fields: list[str] = Field(default_factory=list)
    outdated: bool
    status: JobRecommendationStatus
    generated_at: datetime
    created_at: datetime
    updated_at: datetime
    job: JobRecommendationJobSummary
    reasons: list[JobRecommendationReasonPublic] = Field(default_factory=list)
    feedback: JobRecommendationFeedbackPublic | None = None


class JobRecommendationListData(BaseModel):
    items: list[JobRecommendationPublic]
    page: int
    size: int
    total: int
    total_pages: int


class JobRecommendationRunsData(BaseModel):
    items: list[JobRecommendationRunPublic]
    page: int
    size: int
    total: int
    total_pages: int


class JobRecommendationPolicyData(BaseModel):
    recommendation_type: Literal["RULE_BASED"]
    policy_version: str
    score_range: str = "0~100"
    weights: dict[str, int]
    grades: dict[str, str]
    note: str


class JobRecommendationDeletedData(BaseModel):
    deleted: bool
