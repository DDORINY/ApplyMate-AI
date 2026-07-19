import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ExternalProvider(str, enum.Enum):
    GOOGLE = "GOOGLE"


class ExternalAccountPurpose(str, enum.Enum):
    CALENDAR = "CALENDAR"


class CalendarSyncDirection(str, enum.Enum):
    INTERNAL_TO_GOOGLE = "INTERNAL_TO_GOOGLE"
    GOOGLE_TO_INTERNAL = "GOOGLE_TO_INTERNAL"
    BIDIRECTIONAL = "BIDIRECTIONAL"


class CalendarConnectionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    REAUTH_REQUIRED = "REAUTH_REQUIRED"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"


class CalendarSyncStatus(str, enum.Enum):
    SYNCED = "SYNCED"
    PENDING = "PENDING"
    CONFLICT = "CONFLICT"
    DELETED_INTERNAL = "DELETED_INTERNAL"
    DELETED_EXTERNAL = "DELETED_EXTERNAL"
    FAILED = "FAILED"


class SyncRunStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL_FAILED = "PARTIAL_FAILED"


class SyncErrorCode(str, enum.Enum):
    CALENDAR_CONNECTION_NOT_FOUND = "CALENDAR_CONNECTION_NOT_FOUND"
    CALENDAR_PROVIDER_DISABLED = "CALENDAR_PROVIDER_DISABLED"
    CALENDAR_PROVIDER_UNAVAILABLE = "CALENDAR_PROVIDER_UNAVAILABLE"
    CALENDAR_OAUTH_STATE_INVALID = "CALENDAR_OAUTH_STATE_INVALID"
    CALENDAR_OAUTH_STATE_EXPIRED = "CALENDAR_OAUTH_STATE_EXPIRED"
    CALENDAR_OAUTH_CALLBACK_FAILED = "CALENDAR_OAUTH_CALLBACK_FAILED"
    CALENDAR_TOKEN_ENCRYPTION_FAILED = "CALENDAR_TOKEN_ENCRYPTION_FAILED"
    CALENDAR_TOKEN_REFRESH_FAILED = "CALENDAR_TOKEN_REFRESH_FAILED"
    CALENDAR_REAUTH_REQUIRED = "CALENDAR_REAUTH_REQUIRED"
    CALENDAR_LIST_FAILED = "CALENDAR_LIST_FAILED"
    CALENDAR_NOT_WRITABLE = "CALENDAR_NOT_WRITABLE"
    CALENDAR_SYNC_FAILED = "CALENDAR_SYNC_FAILED"
    CALENDAR_SYNC_CONFLICT = "CALENDAR_SYNC_CONFLICT"
    CALENDAR_MAPPING_NOT_FOUND = "CALENDAR_MAPPING_NOT_FOUND"
    CALENDAR_EXTERNAL_EVENT_NOT_FOUND = "CALENDAR_EXTERNAL_EVENT_NOT_FOUND"
    CALENDAR_SYNC_TOKEN_EXPIRED = "CALENDAR_SYNC_TOKEN_EXPIRED"
    CALENDAR_CONNECTION_FORBIDDEN = "CALENDAR_CONNECTION_FORBIDDEN"


class CalendarOAuthState(Base):
    __tablename__ = "calendar_oauth_states"
    __table_args__ = (
        Index("ix_calendar_oauth_states_state_hash", "state_hash"),
        Index("ix_calendar_oauth_states_expires_at", "expires_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[ExternalProvider] = mapped_column(Enum(ExternalProvider, name="external_provider"), nullable=False)
    state_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    redirect_path: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ExternalAccount(Base):
    __tablename__ = "external_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "purpose", "provider_account_id", name="uq_external_provider_purpose_account"),
        UniqueConstraint("user_id", "provider", "purpose", name="uq_external_user_provider_purpose"),
        Index("ix_external_accounts_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[ExternalProvider] = mapped_column(Enum(ExternalProvider, name="external_provider"), nullable=False)
    purpose: Mapped[ExternalAccountPurpose] = mapped_column(
        Enum(ExternalAccountPurpose, name="external_account_purpose"),
        nullable=False,
        default=ExternalAccountPurpose.CALENDAR,
        server_default=ExternalAccountPurpose.CALENDAR.value,
    )
    provider_account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    scopes: Mapped[str] = mapped_column(Text, nullable=False)
    access_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    token_version: Mapped[str] = mapped_column(String(32), nullable=False, default="v1", server_default="v1")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    connected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    disconnected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    calendar_connections = relationship("CalendarConnection", back_populates="external_account")


class CalendarConnection(Base):
    __tablename__ = "calendar_connections"
    __table_args__ = (
        Index("ix_calendar_connections_user_id", "user_id"),
        Index("ix_calendar_connections_external_account_id", "external_account_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    external_account_id: Mapped[int] = mapped_column(ForeignKey("external_accounts.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[ExternalProvider] = mapped_column(Enum(ExternalProvider, name="external_provider"), nullable=False)
    selected_calendar_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    selected_calendar_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    selected_calendar_timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sync_direction: Mapped[CalendarSyncDirection] = mapped_column(
        Enum(CalendarSyncDirection, name="calendar_sync_direction"),
        nullable=False,
        default=CalendarSyncDirection.INTERNAL_TO_GOOGLE,
        server_default=CalendarSyncDirection.INTERNAL_TO_GOOGLE.value,
    )
    sync_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_sync_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[CalendarConnectionStatus] = mapped_column(
        Enum(CalendarConnectionStatus, name="calendar_connection_status"),
        nullable=False,
        default=CalendarConnectionStatus.ACTIVE,
        server_default=CalendarConnectionStatus.ACTIVE.value,
    )
    connected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    disconnected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    external_account = relationship("ExternalAccount", back_populates="calendar_connections")
    mappings = relationship("CalendarSyncMapping", back_populates="connection")
    sync_runs = relationship("SyncRun", back_populates="connection")


class CalendarSyncMapping(Base):
    __tablename__ = "calendar_sync_mappings"
    __table_args__ = (
        UniqueConstraint("connection_id", "external_event_id", name="uq_calendar_mapping_external_event"),
        UniqueConstraint("connection_id", "schedule_event_id", name="uq_calendar_mapping_schedule_event"),
        Index("ix_calendar_sync_mappings_user_id", "user_id"),
        Index("ix_calendar_sync_mappings_schedule_event_id", "schedule_event_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    connection_id: Mapped[int] = mapped_column(ForeignKey("calendar_connections.id", ondelete="CASCADE"), nullable=False)
    schedule_event_id: Mapped[int] = mapped_column(ForeignKey("schedule_events.id", ondelete="CASCADE"), nullable=False)
    external_calendar_id: Mapped[str] = mapped_column(String(500), nullable=False)
    external_event_id: Mapped[str] = mapped_column(String(500), nullable=False)
    external_etag: Mapped[str | None] = mapped_column(String(255), nullable=True)
    external_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_internal_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_external_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sync_status: Mapped[CalendarSyncStatus] = mapped_column(
        Enum(CalendarSyncStatus, name="calendar_sync_status"),
        nullable=False,
        default=CalendarSyncStatus.PENDING,
        server_default=CalendarSyncStatus.PENDING.value,
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    connection = relationship("CalendarConnection", back_populates="mappings")
    schedule_event = relationship("ScheduleEvent")


class SyncRun(Base):
    __tablename__ = "sync_runs"
    __table_args__ = (Index("ix_sync_runs_user_connection", "user_id", "connection_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    connection_id: Mapped[int] = mapped_column(ForeignKey("calendar_connections.id", ondelete="CASCADE"), nullable=False)
    direction: Mapped[CalendarSyncDirection] = mapped_column(Enum(CalendarSyncDirection, name="calendar_sync_direction"), nullable=False)
    status: Mapped[SyncRunStatus] = mapped_column(Enum(SyncRunStatus, name="sync_run_status"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    updated_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    deleted_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    skipped_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    conflict_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    sync_token_before: Mapped[str | None] = mapped_column(Text, nullable=True)
    sync_token_after: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    connection = relationship("CalendarConnection", back_populates="sync_runs")
    errors = relationship("SyncError", back_populates="sync_run")


class SyncError(Base):
    __tablename__ = "sync_errors"
    __table_args__ = (Index("ix_sync_errors_user_connection", "user_id", "connection_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    connection_id: Mapped[int | None] = mapped_column(ForeignKey("calendar_connections.id", ondelete="SET NULL"), nullable=True)
    sync_run_id: Mapped[int | None] = mapped_column(ForeignKey("sync_runs.id", ondelete="SET NULL"), nullable=True)
    mapping_id: Mapped[int | None] = mapped_column(ForeignKey("calendar_sync_mappings.id", ondelete="SET NULL"), nullable=True)
    error_code: Mapped[SyncErrorCode] = mapped_column(Enum(SyncErrorCode, name="sync_error_code"), nullable=False)
    safe_message: Mapped[str] = mapped_column(String(500), nullable=False)
    retryable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    sync_run = relationship("SyncRun", back_populates="errors")
