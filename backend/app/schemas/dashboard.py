from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


DashboardPeriod = Literal["7d", "30d", "90d", "all", "custom"]


class DashboardSummary(BaseModel):
    total_applications: int
    preparing_applications: int
    in_progress_applications: int
    interview_applications: int
    offer_applications: int
    rejected_applications: int
    withdrawn_applications: int
    closed_applications: int
    week_events: int
    upcoming_deadlines: int
    due_soon_jobs: int


class DashboardApplicationStatusCount(BaseModel):
    group: str
    label: str
    count: int
    percentage: float
    statuses: list[str]


class DashboardApplicationActivity(BaseModel):
    new_applications: int
    status_changes: int
    period_start: datetime | None
    period_end: datetime | None


class DashboardScheduleItem(BaseModel):
    id: int
    title: str
    event_type: str
    status: str
    effective_status: str
    confidence: str
    start_at: datetime
    end_at: datetime
    all_day: bool
    timezone: str
    application_id: int | None
    job_id: int | None
    company_name: str | None = None
    job_title: str | None = None
    location: str | None = None
    online_url: str | None = None
    has_conflict: bool = False
    hours_remaining: int | None = None


class DashboardDeadlineItem(BaseModel):
    kind: Literal["SCHEDULE", "JOB"]
    id: int
    title: str
    due_at: datetime
    hours_remaining: int | None
    company_name: str | None = None
    job_title: str | None = None
    status: str | None = None
    confidence: str | None = None
    link_path: str


class DashboardPreparingApplication(BaseModel):
    id: int
    company_name: str | None
    job_title: str | None
    status: str
    priority: str
    planned_apply_at: datetime | None
    resume_id: int | None
    application_document_id: int | None
    hours_until_planned_apply: int | None
    link_path: str


class DashboardRecentJobAnalysis(BaseModel):
    id: int
    job_id: int
    company_name: str | None
    job_title: str | None
    status: str
    provider: str | None = None
    summary: str | None = None
    technical_skills: list[str] = Field(default_factory=list)
    is_outdated: bool = False
    updated_at: datetime
    link_path: str


class DashboardRecentMatch(BaseModel):
    id: int
    job_id: int
    company_name: str | None
    job_title: str | None
    status: str
    total_score: int
    grade: str
    recommendation_status: str
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    updated_at: datetime
    link_path: str


class DashboardRecentResumeAnalysis(BaseModel):
    id: int
    resume_id: int
    resume_file_id: int
    resume_title: str | None
    filename: str | None
    status: str
    provider: str | None
    summary: str | None
    skills_count: int
    experiences_count: int
    is_outdated: bool
    updated_at: datetime
    link_path: str


class DashboardRecentDocument(BaseModel):
    id: int
    title: str
    document_type: str
    status: str
    company_name: str | None
    job_title: str | None
    current_version_number: int | None
    updated_at: datetime
    link_path: str


class DashboardActivityItem(BaseModel):
    id: str
    activity_type: str
    title: str
    occurred_at: datetime
    link_path: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class DashboardResponse(BaseModel):
    summary: DashboardSummary
    application_status_counts: list[DashboardApplicationStatusCount]
    application_activity: DashboardApplicationActivity
    today_events: list[DashboardScheduleItem]
    week_events: list[DashboardScheduleItem]
    upcoming_deadlines: list[DashboardDeadlineItem]
    due_soon_jobs: list[DashboardDeadlineItem]
    preparing_applications: list[DashboardPreparingApplication]
    recent_job_analyses: list[DashboardRecentJobAnalysis]
    recent_matches: list[DashboardRecentMatch]
    recent_resume_analyses: list[DashboardRecentResumeAnalysis]
    recent_documents: list[DashboardRecentDocument]
    recent_activities: list[DashboardActivityItem]
    generated_at: datetime
    timezone: str
    period: DashboardPeriod
    period_start: datetime | None
    period_end: datetime | None
