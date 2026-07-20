from datetime import datetime

from pydantic import BaseModel, Field

from app.models.job_recommendation import JobRecommendationFeedbackType
from app.models.job_recommendation_automation import (
    RecommendationChangeReason,
    RecommendationChangeType,
    RecommendationConfidence,
    RecommendationNotificationStatus,
    RecommendationNotificationType,
    RecommendationRunFrequency,
    RecommendationRunSkipReason,
)


class JobRecommendationSettingsUpdate(BaseModel):
    enabled: bool | None = None
    frequency: RecommendationRunFrequency | None = None
    preferred_run_hour: int | None = Field(default=None, ge=0, le=23)
    timezone: str | None = Field(default=None, min_length=1, max_length=64)
    minimum_score: int | None = Field(default=None, ge=0, le=100)
    include_jobs_without_analysis: bool | None = None
    exclude_applied_jobs: bool | None = None
    exclude_hidden_jobs: bool | None = None
    notify_new_recommendations: bool | None = None
    notify_score_changes: bool | None = None


class JobRecommendationSettingsPublic(BaseModel):
    id: int
    user_id: int
    enabled: bool
    frequency: RecommendationRunFrequency
    preferred_run_hour: int
    timezone: str
    minimum_score: int
    include_jobs_without_analysis: bool
    exclude_applied_jobs: bool
    exclude_hidden_jobs: bool
    notify_new_recommendations: bool
    notify_score_changes: bool
    last_run_at: datetime | None
    next_run_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobRecommendationRunIfDueRequest(BaseModel):
    force: bool = False


class JobRecommendationRunIfDueData(BaseModel):
    executed: bool
    skip_reason: RecommendationRunSkipReason | None = None
    run_id: int | None = None
    snapshot_id: int | None = None
    recommended_count: int = 0
    new_count: int = 0
    changed_count: int = 0
    removed_count: int = 0
    next_run_at: datetime | None = None
    message: str


class JobRecommendationSnapshotItemPublic(BaseModel):
    id: int
    snapshot_id: int
    recommendation_id: int | None
    job_id: int
    score: int
    grade: str
    rank: int
    blocking_mismatch: bool
    change_type: RecommendationChangeType
    previous_score: int | None
    score_delta: int | None
    previous_grade: str | None
    rank_delta: int | None
    change_reason: RecommendationChangeReason
    reason_summary: list[str] = Field(default_factory=list)
    missing_job_fields: list[str] = Field(default_factory=list)
    data_completeness_score: int
    recommendation_confidence: RecommendationConfidence
    created_at: datetime

    model_config = {"from_attributes": True}


class JobRecommendationSnapshotPublic(BaseModel):
    id: int
    user_id: int
    run_id: int
    profile_hash: str
    policy_version: str
    input_job_count: int
    recommended_count: int
    new_count: int
    changed_count: int
    removed_count: int
    generated_at: datetime
    created_at: datetime
    items: list[JobRecommendationSnapshotItemPublic] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class JobRecommendationSnapshotListData(BaseModel):
    items: list[JobRecommendationSnapshotPublic]
    page: int
    size: int
    total: int
    total_pages: int


class JobRecommendationChangeListData(BaseModel):
    items: list[JobRecommendationSnapshotItemPublic]
    page: int
    size: int
    total: int
    total_pages: int


class RecommendationNotificationUpdate(BaseModel):
    status: RecommendationNotificationStatus


class RecommendationNotificationPublic(BaseModel):
    id: int
    user_id: int
    recommendation_id: int | None
    snapshot_id: int
    snapshot_item_id: int | None
    notification_type: RecommendationNotificationType
    status: RecommendationNotificationStatus
    title: str
    message: str
    payload: dict | None
    expires_at: datetime | None
    read_at: datetime | None
    dismissed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecommendationNotificationListData(BaseModel):
    items: list[RecommendationNotificationPublic]
    page: int
    size: int
    total: int
    total_pages: int


class RecommendationEmptyStateData(BaseModel):
    code: str
    message: str
    cta_label: str
    cta_href: str


class RecommendationListAutomationFilters(BaseModel):
    change_type: RecommendationChangeType | None = None
    feedback_type: JobRecommendationFeedbackType | None = None
    minimum_score: int | None = Field(default=None, ge=0, le=100)
