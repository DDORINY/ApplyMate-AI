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


class ResumePageText(BaseModel):
    page: int
    text: str


class ResumeSectionCandidate(BaseModel):
    section: str
    confidence: float = Field(ge=0, le=1)
    text: str


class ResumeExtractionUpdate(BaseModel):
    edited_text: str = Field(min_length=1, max_length=200_000)


class ResumeExtractionRunPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    extraction_id: int | None
    resume_file_id: int
    status: ResumeExtractionStatus
    input_hash: str
    extractor: str
    extractor_version: str
    started_at: datetime
    completed_at: datetime | None
    error_code: str | None
    error_message: str | None
    page_count: int
    character_count: int
    metadata_json: dict[str, object]
    created_at: datetime


class ResumeExtractionRunListData(BaseModel):
    items: list[ResumeExtractionRunPublic]


class ResumeFileExtractionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_file_id: int
    extraction_status: ResumeExtractionStatus
    status: ResumeExtractionStatus
    raw_text: str | None
    edited_text: str | None
    extracted_text: str | None
    page_texts: list[dict[str, object]]
    section_candidates: list[dict[str, object]]
    page_count: int
    character_count: int
    text_length: int
    input_hash: str
    source_file_hash: str
    parser_version: str
    is_outdated: bool
    is_user_edited: bool
    current_run_id: int | None
    error_code: str | None
    error_message: str | None
    extracted_at: datetime
    created_at: datetime
    updated_at: datetime
