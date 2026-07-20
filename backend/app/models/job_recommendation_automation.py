import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RecommendationRunFrequency(str, enum.Enum):
    MANUAL = "MANUAL"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"


class RecommendationRunSkipReason(str, enum.Enum):
    DISABLED = "DISABLED"
    NOT_DUE = "NOT_DUE"
    PROFILE_MISSING = "PROFILE_MISSING"
    NO_ACTIVE_JOBS = "NO_ACTIVE_JOBS"
    DUPLICATE_INPUT = "DUPLICATE_INPUT"
    ALREADY_RUNNING = "ALREADY_RUNNING"


class RecommendationChangeType(str, enum.Enum):
    NEW = "NEW"
    UNCHANGED = "UNCHANGED"
    SCORE_UP = "SCORE_UP"
    SCORE_DOWN = "SCORE_DOWN"
    GRADE_UP = "GRADE_UP"
    GRADE_DOWN = "GRADE_DOWN"
    REMOVED = "REMOVED"
    OUTDATED = "OUTDATED"


class RecommendationChangeReason(str, enum.Enum):
    PROFILE_UPDATED = "PROFILE_UPDATED"
    JOB_UPDATED = "JOB_UPDATED"
    JOB_ANALYSIS_UPDATED = "JOB_ANALYSIS_UPDATED"
    POLICY_UPDATED = "POLICY_UPDATED"
    FEEDBACK_CHANGED = "FEEDBACK_CHANGED"
    UNKNOWN = "UNKNOWN"


class RecommendationConfidence(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RecommendationNotificationType(str, enum.Enum):
    NEW_HIGH_SCORE_RECOMMENDATION = "NEW_HIGH_SCORE_RECOMMENDATION"
    RECOMMENDATION_SCORE_INCREASED = "RECOMMENDATION_SCORE_INCREASED"
    RECOMMENDATION_GRADE_INCREASED = "RECOMMENDATION_GRADE_INCREASED"
    APPLICATION_DEADLINE_APPROACHING = "APPLICATION_DEADLINE_APPROACHING"
    RECOMMENDATION_BECAME_OUTDATED = "RECOMMENDATION_BECAME_OUTDATED"


class RecommendationNotificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    READ = "READ"
    DISMISSED = "DISMISSED"
    EXPIRED = "EXPIRED"


class JobRecommendationSetting(Base):
    __tablename__ = "job_recommendation_settings"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_job_recommendation_settings_user_id"),
        Index("ix_job_recommendation_settings_next_run", "enabled", "next_run_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    frequency: Mapped[RecommendationRunFrequency] = mapped_column(
        Enum(RecommendationRunFrequency, name="recommendation_run_frequency"),
        nullable=False,
        default=RecommendationRunFrequency.MANUAL,
        server_default=RecommendationRunFrequency.MANUAL.value,
    )
    preferred_run_hour: Mapped[int] = mapped_column(Integer, nullable=False, default=9, server_default="9")
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Seoul", server_default="Asia/Seoul")
    minimum_score: Mapped[int] = mapped_column(Integer, nullable=False, default=50, server_default="50")
    include_jobs_without_analysis: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    exclude_applied_jobs: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    exclude_hidden_jobs: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    notify_new_recommendations: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    notify_score_changes: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class JobRecommendationSnapshot(Base):
    __tablename__ = "job_recommendation_snapshots"
    __table_args__ = (
        Index("ix_job_recommendation_snapshots_user_generated", "user_id", "generated_at"),
        Index("ix_job_recommendation_snapshots_user_run", "user_id", "run_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    run_id: Mapped[int] = mapped_column(ForeignKey("job_recommendation_runs.id", ondelete="CASCADE"), nullable=False)
    profile_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    policy_version: Mapped[str] = mapped_column(String(40), nullable=False)
    input_job_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    recommended_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    new_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    changed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    removed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    items = relationship("JobRecommendationSnapshotItem", back_populates="snapshot", cascade="all, delete-orphan")
    notifications = relationship("RecommendationNotificationCandidate", back_populates="snapshot")


class JobRecommendationSnapshotItem(Base):
    __tablename__ = "job_recommendation_snapshot_items"
    __table_args__ = (
        Index("ix_job_recommendation_snapshot_items_snapshot_rank", "snapshot_id", "rank"),
        Index("ix_job_recommendation_snapshot_items_recommendation", "recommendation_id"),
        UniqueConstraint("snapshot_id", "job_id", name="uq_job_recommendation_snapshot_items_snapshot_job"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("job_recommendation_snapshots.id", ondelete="CASCADE"), nullable=False)
    recommendation_id: Mapped[int | None] = mapped_column(ForeignKey("job_recommendations.id", ondelete="SET NULL"), nullable=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    grade: Mapped[str] = mapped_column(String(40), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    blocking_mismatch: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    change_type: Mapped[RecommendationChangeType] = mapped_column(
        Enum(RecommendationChangeType, name="recommendation_change_type"), nullable=False
    )
    previous_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_delta: Mapped[int | None] = mapped_column(Integer, nullable=True)
    previous_grade: Mapped[str | None] = mapped_column(String(40), nullable=True)
    rank_delta: Mapped[int | None] = mapped_column(Integer, nullable=True)
    change_reason: Mapped[RecommendationChangeReason] = mapped_column(
        Enum(RecommendationChangeReason, name="recommendation_change_reason"),
        nullable=False,
        default=RecommendationChangeReason.UNKNOWN,
        server_default=RecommendationChangeReason.UNKNOWN.value,
    )
    reason_summary: Mapped[list | None] = mapped_column(JSON, nullable=True)
    missing_job_fields: Mapped[list | None] = mapped_column(JSON, nullable=True)
    data_completeness_score: Mapped[int] = mapped_column(Integer, nullable=False, default=100, server_default="100")
    recommendation_confidence: Mapped[RecommendationConfidence] = mapped_column(
        Enum(RecommendationConfidence, name="recommendation_confidence"),
        nullable=False,
        default=RecommendationConfidence.HIGH,
        server_default=RecommendationConfidence.HIGH.value,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    snapshot = relationship("JobRecommendationSnapshot", back_populates="items")
    notification_candidates = relationship("RecommendationNotificationCandidate", back_populates="snapshot_item")


class RecommendationNotificationCandidate(Base):
    __tablename__ = "recommendation_notification_candidates"
    __table_args__ = (
        Index("ix_recommendation_notifications_user_status", "user_id", "status"),
        Index("ix_recommendation_notifications_user_created", "user_id", "created_at"),
        UniqueConstraint(
            "user_id",
            "snapshot_id",
            "recommendation_id",
            "notification_type",
            name="uq_recommendation_notifications_unique_candidate",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recommendation_id: Mapped[int | None] = mapped_column(ForeignKey("job_recommendations.id", ondelete="CASCADE"), nullable=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("job_recommendation_snapshots.id", ondelete="CASCADE"), nullable=False)
    snapshot_item_id: Mapped[int | None] = mapped_column(ForeignKey("job_recommendation_snapshot_items.id", ondelete="SET NULL"), nullable=True)
    notification_type: Mapped[RecommendationNotificationType] = mapped_column(
        Enum(RecommendationNotificationType, name="recommendation_notification_type"), nullable=False
    )
    status: Mapped[RecommendationNotificationStatus] = mapped_column(
        Enum(RecommendationNotificationStatus, name="recommendation_notification_status"),
        nullable=False,
        default=RecommendationNotificationStatus.PENDING,
        server_default=RecommendationNotificationStatus.PENDING.value,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dismissed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    snapshot = relationship("JobRecommendationSnapshot", back_populates="notifications")
    snapshot_item = relationship("JobRecommendationSnapshotItem", back_populates="notification_candidates")
