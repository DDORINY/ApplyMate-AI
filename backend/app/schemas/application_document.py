from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.application_document import (
    ApplicationDocumentStatus,
    ApplicationDocumentTone,
    ApplicationDocumentType,
    GenerationRunStatus,
)


class ApplicationDocumentSourceReference(BaseModel):
    source_type: str
    source_id: str
    field_path: str | None = None
    evidence_text: str = Field(min_length=1, max_length=2000)
    page_number: int | None = None
    section: str | None = None
    start_offset: int | None = None
    end_offset: int | None = None


class ApplicationDocumentBlock(BaseModel):
    sequence: int = Field(ge=1)
    text: str = Field(min_length=1)
    source_references: list[ApplicationDocumentSourceReference] = Field(min_length=1)
    confidence: float = Field(default=0.7, ge=0, le=1)
    requires_review: bool = False
    review_reason: str | None = None


class ApplicationDocumentStructuredData(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    document_type: ApplicationDocumentType
    content: str = Field(min_length=1)
    blocks: list[ApplicationDocumentBlock] = Field(min_length=1)
    warnings: list[str] = Field(default_factory=list)
    requires_review: bool = False
    character_count_candidate: int | None = None


class ApplicationDocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    document_type: ApplicationDocumentType
    job_id: int | None = None
    resume_id: int | None = None
    resume_file_id: int | None = None
    resume_analysis_id: int | None = None
    job_analysis_id: int | None = None
    job_match_id: int | None = None
    question: str | None = Field(default=None, max_length=2000)
    instructions: str | None = Field(default=None, max_length=4000)
    tone: ApplicationDocumentTone = ApplicationDocumentTone.PROFESSIONAL
    language: str = Field(default="ko", max_length=20)
    character_limit: int | None = Field(default=None, ge=1, le=10000)
    minimum_character_count: int | None = Field(default=None, ge=1, le=10000)
    target_character_count: int | None = Field(default=None, ge=1, le=10000)
    maximum_character_count: int | None = Field(default=None, ge=1, le=10000)
    focus_points: list[str] = Field(default_factory=list)
    avoid_phrases: list[str] = Field(default_factory=list)
    settings: dict[str, object] = Field(default_factory=dict)

    @field_validator("focus_points", "avoid_phrases")
    @classmethod
    def trim_string_list(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item and item.strip()][:20]


class ApplicationDocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    question: str | None = Field(default=None, max_length=2000)
    instructions: str | None = Field(default=None, max_length=4000)
    tone: ApplicationDocumentTone | None = None
    language: str | None = Field(default=None, max_length=20)
    character_limit: int | None = Field(default=None, ge=1, le=10000)
    minimum_character_count: int | None = Field(default=None, ge=1, le=10000)
    target_character_count: int | None = Field(default=None, ge=1, le=10000)
    maximum_character_count: int | None = Field(default=None, ge=1, le=10000)
    focus_points: list[str] | None = None
    avoid_phrases: list[str] | None = None
    settings: dict[str, object] | None = None


class ApplicationDocumentGenerateRequest(BaseModel):
    instructions: str | None = Field(default=None, max_length=4000)
    question: str | None = Field(default=None, max_length=2000)
    character_limit: int | None = Field(default=None, ge=1, le=10000)
    tone: ApplicationDocumentTone | None = None
    focus_points: list[str] | None = None


class ApplicationDocumentVersionCreate(BaseModel):
    content: str = Field(min_length=1)
    content_blocks: list[ApplicationDocumentBlock] | None = None
    change_summary: str | None = Field(default=None, max_length=300)


class ApplicationDocumentDuplicateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)


class ApplicationDocumentVersionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    user_id: int
    version_number: int
    content: str
    content_blocks: list[dict[str, object]]
    character_count: int
    character_count_without_spaces: int
    word_count: int
    paragraph_count: int
    limit_exceeded: bool
    is_ai_generated: bool
    is_user_edited: bool
    generation_run_id: int | None
    change_summary: str | None
    created_at: datetime


class ApplicationDocumentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    job_id: int | None
    resume_id: int | None
    resume_file_id: int | None
    resume_analysis_id: int | None
    job_analysis_id: int | None
    job_match_id: int | None
    document_type: ApplicationDocumentType
    title: str
    question: str | None
    instructions: str | None
    tone: ApplicationDocumentTone
    language: str
    character_limit: int | None
    minimum_character_count: int | None
    target_character_count: int | None
    maximum_character_count: int | None
    focus_points: list[str]
    avoid_phrases: list[str]
    settings: dict[str, object]
    status: ApplicationDocumentStatus
    current_version_number: int | None
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    current_version: ApplicationDocumentVersionPublic | None = None


class ApplicationDocumentListData(BaseModel):
    items: list[ApplicationDocumentPublic]
    total: int
    page: int
    size: int


class ApplicationDocumentSourcePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    version_id: int
    user_id: int
    source_type: str
    source_id: str
    source_version: str | None
    source_hash: str
    field_path: str | None
    source_snapshot: dict[str, object]
    evidence: dict[str, object]
    created_at: datetime


class GenerationRunPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    user_id: int
    status: GenerationRunStatus
    provider: str
    model: str | None
    prompt_version: str
    schema_version: str
    input_hash: str
    settings: dict[str, object]
    started_at: datetime
    completed_at: datetime | None
    error_code: str | None
    safe_error_message: str | None
    usage_metadata: dict[str, object]
    result_snapshot: dict[str, object] | None
    created_at: datetime


class DocumentProviderStatus(BaseModel):
    active_provider: str
    enabled: bool
    model: str | None
    generation_available: bool
