import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
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
