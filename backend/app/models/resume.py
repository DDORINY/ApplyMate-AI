import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ResumeSourceType(str, enum.Enum):
    USER_UPLOAD = "USER_UPLOAD"
    MANUAL = "MANUAL"


class Resume(Base):
    __tablename__ = "resumes"
    __table_args__ = (
        Index("ix_resumes_user_id", "user_id"),
        Index("ix_resumes_user_default", "user_id", "is_default"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[ResumeSourceType] = mapped_column(
        Enum(ResumeSourceType, name="resume_source_type"),
        nullable=False,
        default=ResumeSourceType.USER_UPLOAD,
        server_default=ResumeSourceType.USER_UPLOAD.value,
    )
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    files = relationship("ResumeFile", back_populates="resume", cascade="all, delete-orphan")


class ResumeFile(Base):
    __tablename__ = "resume_files"
    __table_args__ = (
        Index("ix_resume_files_resume_id", "resume_id"),
        Index("ix_resume_files_user_id", "user_id"),
        UniqueConstraint("user_id", "file_hash", name="uq_resume_files_user_file_hash"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    storage_path: Mapped[str] = mapped_column(String(700), nullable=False)
    content_type: Mapped[str] = mapped_column(String(160), nullable=False)
    file_extension: Mapped[str] = mapped_column(String(20), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    resume = relationship("Resume", back_populates="files")
    extraction = relationship(
        "ResumeFileExtraction",
        back_populates="resume_file",
        cascade="all, delete-orphan",
        uselist=False,
    )


class ResumeExtractionStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TEXT_NOT_FOUND = "TEXT_NOT_FOUND"
    OCR_REQUIRED = "OCR_REQUIRED"


class ResumeFileExtraction(Base):
    __tablename__ = "resume_file_extractions"
    __table_args__ = (
        Index("ix_resume_file_extractions_user_id", "user_id"),
        UniqueConstraint("resume_file_id", name="uq_resume_file_extractions_resume_file_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resume_file_id: Mapped[int] = mapped_column(
        ForeignKey("resume_files.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    extraction_status: Mapped[ResumeExtractionStatus] = mapped_column(
        Enum(ResumeExtractionStatus, name="resume_extraction_status"),
        nullable=False,
        default=ResumeExtractionStatus.PENDING,
        server_default=ResumeExtractionStatus.PENDING.value,
    )
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    edited_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_texts: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    section_candidates: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    character_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    input_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    is_outdated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    is_user_edited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    current_run_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    resume_file = relationship("ResumeFile", back_populates="extraction")
    runs = relationship("ResumeExtractionRun", back_populates="extraction", cascade="all, delete-orphan")

    @property
    def status(self) -> ResumeExtractionStatus:
        return self.extraction_status

    @property
    def extracted_text(self) -> str | None:
        return self.edited_text if self.is_user_edited and self.edited_text is not None else self.raw_text

    @property
    def text_length(self) -> int:
        return self.character_count

    @property
    def parser_version(self) -> str:
        return "v0.3.1-basic"

    @property
    def source_file_hash(self) -> str:
        return self.input_hash


class ResumeExtractionRun(Base):
    __tablename__ = "resume_extraction_runs"
    __table_args__ = (
        Index("ix_resume_extraction_runs_extraction_id", "extraction_id"),
        Index("ix_resume_extraction_runs_user_id", "user_id"),
        Index("ix_resume_extraction_runs_resume_file_id", "resume_file_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    extraction_id: Mapped[int | None] = mapped_column(
        ForeignKey("resume_file_extractions.id", ondelete="CASCADE"),
        nullable=True,
    )
    resume_file_id: Mapped[int] = mapped_column(
        ForeignKey("resume_files.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[ResumeExtractionStatus] = mapped_column(
        Enum(ResumeExtractionStatus, name="resume_extraction_status"),
        nullable=False,
    )
    input_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    extractor: Mapped[str] = mapped_column(String(80), nullable=False)
    extractor_version: Mapped[str] = mapped_column(String(40), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    character_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    extraction = relationship("ResumeFileExtraction", back_populates="runs")


Index(
    "uq_resumes_one_default_per_user",
    Resume.user_id,
    unique=True,
    postgresql_where=Resume.is_default.is_(True),
    sqlite_where=Resume.is_default.is_(True),
)
