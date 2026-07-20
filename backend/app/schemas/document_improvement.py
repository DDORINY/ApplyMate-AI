from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from app.models.document_improvement import (
    DocumentImprovementActionType,
    DocumentImprovementChangeType,
    DocumentImprovementRiskLevel,
    DocumentImprovementRunStatus,
    DocumentImprovementSourceType,
    DocumentImprovementSuggestionStatus,
    DocumentImprovementType,
)


class DocumentImprovementEvidence(BaseModel):
    source_type: DocumentImprovementSourceType
    source_id: str
    source_text: str = Field(min_length=1, max_length=1000)


class DocumentImprovementSentenceSuggestionData(BaseModel):
    id: str | None = None
    paragraph_index: int = Field(default=0, ge=0)
    sentence_index: int = Field(default=0, ge=0)
    original_text: str = Field(min_length=1)
    suggested_text: str = Field(min_length=1)
    change_type: DocumentImprovementChangeType
    reason: str = Field(min_length=1)
    evidence: list[DocumentImprovementEvidence] = Field(default_factory=list)
    risk_level: DocumentImprovementRiskLevel = DocumentImprovementRiskLevel.LOW
    selected: bool = True


class DocumentImprovementStructuredData(BaseModel):
    summary: str
    overall_feedback: str
    suggested_title: str | None = None
    suggested_content: str
    sentence_suggestions: list[DocumentImprovementSentenceSuggestionData]
    warnings: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    used_sources: list[DocumentImprovementEvidence] = Field(default_factory=list)
    confidence: dict[str, float] = Field(default_factory=dict)


class DocumentImprovementCreateRequest(BaseModel):
    improvement_type: DocumentImprovementType
    custom_instruction: str | None = Field(default=None, max_length=2000)
    base_version_id: int | None = None
    target_min_length: int | None = Field(default=None, ge=1, le=10000)
    target_max_length: int | None = Field(default=None, ge=1, le=10000)
    target_tone: str | None = Field(default=None, max_length=80)
    source_ids: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_lengths(self):
        if self.target_min_length and self.target_max_length and self.target_min_length > self.target_max_length:
            raise ValueError("target_min_length must be less than or equal to target_max_length")
        if self.improvement_type == DocumentImprovementType.CUSTOM and not self.custom_instruction:
            raise ValueError("custom_instruction is required for CUSTOM improvement")
        return self


class DocumentImprovementSuggestionUpdate(BaseModel):
    status: DocumentImprovementSuggestionStatus | None = None
    selected: bool | None = None


class DocumentImprovementApplyRequest(BaseModel):
    apply_all: bool = False
    suggestion_ids: list[int] = Field(default_factory=list)
    version_title: str | None = Field(default=None, max_length=200)


class DocumentImprovementSourcePublic(BaseModel):
    id: int
    run_id: int
    source_type: DocumentImprovementSourceType
    source_id: str
    source_hash: str
    source_snapshot: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentImprovementSuggestionPublic(BaseModel):
    id: int
    run_id: int
    paragraph_index: int
    sentence_index: int
    original_text: str
    suggested_text: str
    change_type: DocumentImprovementChangeType
    reason: str
    evidence: list[dict[str, Any]]
    risk_level: DocumentImprovementRiskLevel
    status: DocumentImprovementSuggestionStatus
    selected: bool
    applied_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentImprovementActionPublic(BaseModel):
    id: int
    user_id: int
    run_id: int
    suggestion_id: int | None
    action: DocumentImprovementActionType
    previous_text: str | None
    new_text: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentImprovementRunPublic(BaseModel):
    id: int
    user_id: int
    application_document_id: int
    base_version_id: int
    result_version_id: int | None
    status: DocumentImprovementRunStatus
    improvement_type: DocumentImprovementType
    custom_instruction: str | None
    target_min_length: int | None
    target_max_length: int | None
    target_tone: str | None
    provider: str
    model: str | None
    prompt_version: str
    schema_version: str
    input_hash: str
    source_hash: str
    outdated: bool
    started_at: datetime
    completed_at: datetime | None
    error_code: str | None
    safe_error_message: str | None
    overall_feedback: str | None
    suggested_title: str | None
    suggested_content: str | None
    warnings: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    confidence: dict[str, float] = Field(default_factory=dict)
    usage_metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    suggestions: list[DocumentImprovementSuggestionPublic] = Field(default_factory=list)
    sources: list[DocumentImprovementSourcePublic] = Field(default_factory=list)
    actions: list[DocumentImprovementActionPublic] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class DocumentImprovementListData(BaseModel):
    items: list[DocumentImprovementRunPublic]
    page: int
    size: int
    total: int
    total_pages: int


class DocumentImprovementApplyData(BaseModel):
    applied: bool
    version_id: int
    version_number: int
    applied_suggestion_count: int


class DocumentImprovementRejectData(BaseModel):
    rejected: Literal[True] = True


class DocumentImprovementDeletedData(BaseModel):
    deleted: bool
