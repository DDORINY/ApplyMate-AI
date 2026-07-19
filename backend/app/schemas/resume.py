from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.resume import ResumeExtractionStatus, ResumeSourceType


class ResumeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    source_type: ResumeSourceType = ResumeSourceType.USER_UPLOAD
    is_default: bool = False


class ResumeUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    is_default: bool | None = None


class ResumeFilePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    original_filename: str
    content_type: str
    file_extension: str
    file_size: int
    file_hash: str
    uploaded_at: datetime
    created_at: datetime


class ResumePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    source_type: ResumeSourceType
    is_default: bool
    created_at: datetime
    updated_at: datetime
    files: list[ResumeFilePublic] = []


class ResumeListData(BaseModel):
    items: list[ResumePublic]
    page: int
    size: int
    total: int
    total_pages: int


class ResumeDeletedData(BaseModel):
    deleted: bool


class ResumeFileDeletedData(BaseModel):
    deleted: bool


class ResumeFileExtractionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_file_id: int
    status: ResumeExtractionStatus
    extracted_text: str | None
    text_length: int
    parser_version: str
    source_file_hash: str
    error_code: str | None
    error_message: str | None
    extracted_at: datetime
    created_at: datetime
    updated_at: datetime
