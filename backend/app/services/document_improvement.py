import hashlib
import json
from datetime import UTC, datetime
from math import ceil

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.document_improvement_prompt import (
    DOCUMENT_IMPROVEMENT_PROMPT_VERSION,
    DOCUMENT_IMPROVEMENT_SCHEMA_VERSION,
    DOCUMENT_IMPROVEMENT_SYSTEM_PROMPT,
    build_document_improvement_prompt,
)
from app.ai.providers import get_ai_provider
from app.core.config import settings
from app.core.exceptions import AppError
from app.models.application_document import ApplicationDocumentStatus, ApplicationDocumentVersion
from app.models.document_improvement import (
    DocumentImprovementAction,
    DocumentImprovementActionType,
    DocumentImprovementRun,
    DocumentImprovementRunStatus,
    DocumentImprovementSource,
    DocumentImprovementSourceType,
    DocumentImprovementSuggestion,
    DocumentImprovementSuggestionStatus,
)
from app.repositories.document_improvement import DocumentImprovementRepository
from app.schemas.document_improvement import (
    DocumentImprovementActionPublic,
    DocumentImprovementApplyData,
    DocumentImprovementApplyRequest,
    DocumentImprovementCreateRequest,
    DocumentImprovementDeletedData,
    DocumentImprovementListData,
    DocumentImprovementRejectData,
    DocumentImprovementRunPublic,
    DocumentImprovementSourcePublic,
    DocumentImprovementStructuredData,
    DocumentImprovementSuggestionPublic,
    DocumentImprovementSuggestionUpdate,
)
from app.services.application_document import _content_counts


class DocumentImprovementService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = DocumentImprovementRepository(session)

    async def create_run(self, user_id: int, document_id: int, payload: DocumentImprovementCreateRequest) -> DocumentImprovementRunPublic:
        document = await self.repository.get_document(user_id, document_id)
        if not document:
            raise AppError("DOCUMENT_NOT_FOUND", "지원 문서를 찾을 수 없습니다.", 404)
        base_version = (
            await self.repository.get_version(user_id, document_id, payload.base_version_id)
            if payload.base_version_id
            else await self.repository.latest_version(user_id, document_id)
        )
        if not base_version:
            raise AppError("DOCUMENT_IMPROVEMENT_BASE_VERSION_NOT_FOUND", "개선 기준 문서 버전을 찾을 수 없습니다.", 404)
        if payload.target_min_length and payload.target_max_length and payload.target_min_length > payload.target_max_length:
            raise AppError("DOCUMENT_IMPROVEMENT_INVALID_LENGTH", "목표 글자 수 범위가 올바르지 않습니다.", 400)

        sources = self._build_sources(base_version, payload)
        source_hash = _hash(sources)
        input_hash = _hash(
            {
                "base_version_id": base_version.id,
                "content": base_version.content,
                "request": payload.model_dump(mode="json"),
                "source_hash": source_hash,
                "prompt_version": DOCUMENT_IMPROVEMENT_PROMPT_VERSION,
                "schema_version": DOCUMENT_IMPROVEMENT_SCHEMA_VERSION,
            }
        )
        provider = get_ai_provider(settings)
        run = DocumentImprovementRun(
            user_id=user_id,
            application_document_id=document.id,
            base_version_id=base_version.id,
            status=DocumentImprovementRunStatus.PROCESSING,
            improvement_type=payload.improvement_type,
            custom_instruction=payload.custom_instruction,
            target_min_length=payload.target_min_length,
            target_max_length=payload.target_max_length,
            target_tone=payload.target_tone,
            provider=provider.provider,
            model=provider.model,
            prompt_version=DOCUMENT_IMPROVEMENT_PROMPT_VERSION,
            schema_version=DOCUMENT_IMPROVEMENT_SCHEMA_VERSION,
            input_hash=input_hash,
            source_hash=source_hash,
            started_at=datetime.now(UTC),
            usage_metadata={},
        )
        self.session.add(run)
        await self.session.flush()
        for source in sources:
            self.session.add(
                DocumentImprovementSource(
                    run_id=run.id,
                    source_type=source["source_type"],
                    source_id=str(source["source_id"]),
                    source_hash=_hash(source),
                    source_snapshot={"text": source["text"][:2000]},
                )
            )
        prompt = build_document_improvement_prompt(
            title=document.title,
            current_content=base_version.content,
            improvement_type=payload.improvement_type.value,
            custom_instruction=payload.custom_instruction,
            target_min_length=payload.target_min_length,
            target_max_length=payload.target_max_length,
            target_tone=payload.target_tone,
            sources=sources,
        )
        try:
            result = await provider.improve_application_document(
                system_prompt=DOCUMENT_IMPROVEMENT_SYSTEM_PROMPT,
                user_prompt=prompt,
                response_schema=DocumentImprovementStructuredData,
            )
            data = result.parsed_data
            if not isinstance(data, DocumentImprovementStructuredData):
                data = DocumentImprovementStructuredData.model_validate(data.model_dump())
            warnings = [*data.warnings, *self._fact_warnings(data)]
            review_required = bool(warnings or data.missing_information)
            run.status = DocumentImprovementRunStatus.REVIEW_REQUIRED if review_required else DocumentImprovementRunStatus.COMPLETED
            run.model = result.model
            run.completed_at = datetime.now(UTC)
            run.overall_feedback = data.overall_feedback
            run.suggested_title = data.suggested_title
            run.suggested_content = data.suggested_content
            run.warnings = warnings
            run.missing_information = data.missing_information
            run.confidence = data.confidence
            run.usage_metadata = {
                "request_id": result.request_id,
                "prompt_tokens": result.prompt_tokens,
                "completion_tokens": result.completion_tokens,
                "total_tokens": result.total_tokens,
                "latency_ms": result.latency_ms,
            }
            for suggestion in data.sentence_suggestions:
                self.session.add(
                    DocumentImprovementSuggestion(
                        run_id=run.id,
                        paragraph_index=suggestion.paragraph_index,
                        sentence_index=suggestion.sentence_index,
                        original_text=suggestion.original_text,
                        suggested_text=suggestion.suggested_text,
                        change_type=suggestion.change_type,
                        reason=suggestion.reason,
                        evidence=[item.model_dump(mode="json") for item in suggestion.evidence],
                        risk_level=suggestion.risk_level,
                        selected=suggestion.selected,
                    )
                )
            await self.session.commit()
        except AppError as exc:
            run.status = DocumentImprovementRunStatus.FAILED
            run.error_code = exc.code
            run.safe_error_message = exc.message[:500]
            run.completed_at = datetime.now(UTC)
            await self.session.commit()
            raise
        return await self.get_run(user_id, document_id, run.id)

    async def list_runs(self, user_id: int, document_id: int, page: int, size: int) -> DocumentImprovementListData:
        document = await self.repository.get_document(user_id, document_id)
        if not document:
            raise AppError("DOCUMENT_NOT_FOUND", "지원 문서를 찾을 수 없습니다.", 404)
        runs, total = await self.repository.list_runs(user_id, document_id, page, size)
        return DocumentImprovementListData(
            items=[self._public(run) for run in runs],
            page=page,
            size=size,
            total=total,
            total_pages=ceil(total / size) if total else 0,
        )

    async def get_run(self, user_id: int, document_id: int, run_id: int) -> DocumentImprovementRunPublic:
        run = await self._get_run(user_id, document_id, run_id)
        await self._mark_outdated_if_needed(user_id, document_id, run)
        return self._public(run)

    async def retry_run(self, user_id: int, document_id: int, run_id: int) -> DocumentImprovementRunPublic:
        run = await self._get_run(user_id, document_id, run_id)
        if run.status == DocumentImprovementRunStatus.APPLIED or run.result_version_id:
            raise AppError("DOCUMENT_IMPROVEMENT_ALREADY_APPLIED", "이미 적용된 개선 실행은 재시도할 수 없습니다.", 409)
        payload = DocumentImprovementCreateRequest(
            improvement_type=run.improvement_type,
            custom_instruction=run.custom_instruction,
            base_version_id=run.base_version_id,
            target_min_length=run.target_min_length,
            target_max_length=run.target_max_length,
            target_tone=run.target_tone,
        )
        return await self.create_run(user_id, document_id, payload)

    async def update_suggestion(
        self,
        user_id: int,
        document_id: int,
        run_id: int,
        suggestion_id: int,
        payload: DocumentImprovementSuggestionUpdate,
    ) -> DocumentImprovementSuggestionPublic:
        run = await self._get_run(user_id, document_id, run_id)
        suggestion = await self.repository.get_suggestion(run.id, suggestion_id)
        if not suggestion:
            raise AppError("DOCUMENT_IMPROVEMENT_SUGGESTION_NOT_FOUND", "개선 제안을 찾을 수 없습니다.", 404)
        if payload.status:
            if payload.status == DocumentImprovementSuggestionStatus.APPLIED:
                raise AppError("DOCUMENT_IMPROVEMENT_INVALID_REQUEST", "제안 적용 상태는 실행 적용 API로만 변경할 수 있습니다.", 400)
            suggestion.status = payload.status
            if payload.status in {DocumentImprovementSuggestionStatus.APPROVED, DocumentImprovementSuggestionStatus.REJECTED}:
                self.session.add(
                    DocumentImprovementAction(
                        user_id=user_id,
                        run_id=run.id,
                        suggestion_id=suggestion.id,
                        action=(
                            DocumentImprovementActionType.SUGGESTION_APPROVED
                            if payload.status == DocumentImprovementSuggestionStatus.APPROVED
                            else DocumentImprovementActionType.SUGGESTION_REJECTED
                        ),
                        previous_text=suggestion.original_text,
                        new_text=suggestion.suggested_text,
                    )
                )
        if payload.selected is not None:
            suggestion.selected = payload.selected
        await self.session.commit()
        await self.session.refresh(suggestion)
        return DocumentImprovementSuggestionPublic.model_validate(suggestion)

    async def apply_run(
        self,
        user_id: int,
        document_id: int,
        run_id: int,
        payload: DocumentImprovementApplyRequest,
    ) -> DocumentImprovementApplyData:
        document = await self.repository.get_document(user_id, document_id)
        if not document:
            raise AppError("DOCUMENT_NOT_FOUND", "지원 문서를 찾을 수 없습니다.", 404)
        run = await self._get_run(user_id, document_id, run_id)
        await self._mark_outdated_if_needed(user_id, document_id, run)
        if run.outdated:
            raise AppError("DOCUMENT_IMPROVEMENT_OUTDATED", "기준 문서 버전이 최신이 아니므로 바로 적용할 수 없습니다.", 409)
        if run.result_version_id or run.status == DocumentImprovementRunStatus.APPLIED:
            raise AppError("DOCUMENT_IMPROVEMENT_ALREADY_APPLIED", "이미 적용된 개선 실행입니다.", 409)
        selected = [
            suggestion
            for suggestion in run.suggestions
            if (payload.apply_all or suggestion.id in payload.suggestion_ids or suggestion.selected)
            and suggestion.status != DocumentImprovementSuggestionStatus.REJECTED
        ]
        if not selected:
            raise AppError("DOCUMENT_IMPROVEMENT_INVALID_REQUEST", "적용할 개선 제안이 없습니다.", 400)
        base_version = await self.repository.get_version(user_id, document_id, run.base_version_id)
        if not base_version:
            raise AppError("DOCUMENT_IMPROVEMENT_BASE_VERSION_NOT_FOUND", "개선 기준 문서 버전을 찾을 수 없습니다.", 404)
        content = base_version.content
        for suggestion in selected:
            content = content.replace(suggestion.original_text, suggestion.suggested_text, 1)
        next_number = await self.repository.latest_version_number(document.id) + 1
        version = ApplicationDocumentVersion(
            document_id=document.id,
            user_id=user_id,
            version_number=next_number,
            content=content,
            content_blocks=[],
            is_ai_generated=True,
            is_user_edited=False,
            change_summary=payload.version_title or f"AI 개선본: {run.improvement_type.value}, {len(selected)}개 제안 적용",
            **_content_counts(content, document.character_limit or document.maximum_character_count),
        )
        self.session.add(version)
        await self.session.flush()
        for suggestion in selected:
            suggestion.status = DocumentImprovementSuggestionStatus.APPLIED
            suggestion.applied_at = datetime.now(UTC)
        run.result_version_id = version.id
        run.status = DocumentImprovementRunStatus.APPLIED
        document.current_version_number = next_number
        document.status = ApplicationDocumentStatus.REVIEW_REQUIRED if version.limit_exceeded else ApplicationDocumentStatus.COMPLETED
        self.session.add(
            DocumentImprovementAction(
                user_id=user_id,
                run_id=run.id,
                action=DocumentImprovementActionType.RUN_APPLIED,
                previous_text=base_version.content,
                new_text=content,
            )
        )
        await self.session.commit()
        return DocumentImprovementApplyData(
            applied=True,
            version_id=version.id,
            version_number=version.version_number,
            applied_suggestion_count=len(selected),
        )

    async def reject_run(self, user_id: int, document_id: int, run_id: int) -> DocumentImprovementRejectData:
        run = await self._get_run(user_id, document_id, run_id)
        run.status = DocumentImprovementRunStatus.REJECTED
        for suggestion in run.suggestions:
            if suggestion.status == DocumentImprovementSuggestionStatus.PENDING:
                suggestion.status = DocumentImprovementSuggestionStatus.REJECTED
        self.session.add(DocumentImprovementAction(user_id=user_id, run_id=run.id, action=DocumentImprovementActionType.RUN_REJECTED))
        await self.session.commit()
        return DocumentImprovementRejectData()

    async def delete_run(self, user_id: int, document_id: int, run_id: int) -> DocumentImprovementDeletedData:
        run = await self._get_run(user_id, document_id, run_id)
        if run.result_version_id:
            raise AppError("DOCUMENT_IMPROVEMENT_ALREADY_APPLIED", "적용된 개선 실행은 삭제할 수 없습니다.", 409)
        await self.session.delete(run)
        await self.session.commit()
        return DocumentImprovementDeletedData(deleted=True)

    async def _get_run(self, user_id: int, document_id: int, run_id: int) -> DocumentImprovementRun:
        run = await self.repository.get_run(user_id, document_id, run_id)
        if not run:
            raise AppError("DOCUMENT_IMPROVEMENT_NOT_FOUND", "개선 실행을 찾을 수 없습니다.", 404)
        return run

    async def _mark_outdated_if_needed(self, user_id: int, document_id: int, run: DocumentImprovementRun) -> None:
        latest = await self.repository.latest_version(user_id, document_id)
        if latest and latest.id != run.base_version_id and not run.result_version_id:
            run.outdated = True
            await self.session.commit()

    def _build_sources(self, base_version: ApplicationDocumentVersion, payload: DocumentImprovementCreateRequest) -> list[dict[str, object]]:
        sources: list[dict[str, object]] = [
            {
                "source_type": DocumentImprovementSourceType.CURRENT_DOCUMENT,
                "source_id": str(base_version.id),
                "text": base_version.content[:2000],
            }
        ]
        if payload.custom_instruction:
            sources.append(
                {
                    "source_type": DocumentImprovementSourceType.USER_INSTRUCTION,
                    "source_id": "request",
                    "text": payload.custom_instruction[:2000],
                }
            )
        return sources

    def _fact_warnings(self, data: DocumentImprovementStructuredData) -> list[str]:
        warnings: list[str] = []
        risky_terms = ["30%", "5년", "Kubernetes", "매출", "사용자 수"]
        for suggestion in data.sentence_suggestions:
            if any(term in suggestion.suggested_text and term not in suggestion.original_text for term in risky_terms):
                if not suggestion.evidence:
                    warnings.append("근거 없는 핵심 사실 또는 수치 후보가 감지되어 검토가 필요합니다.")
        return warnings

    def _public(self, run: DocumentImprovementRun) -> DocumentImprovementRunPublic:
        return DocumentImprovementRunPublic(
            id=run.id,
            user_id=run.user_id,
            application_document_id=run.application_document_id,
            base_version_id=run.base_version_id,
            result_version_id=run.result_version_id,
            status=run.status,
            improvement_type=run.improvement_type,
            custom_instruction=run.custom_instruction,
            target_min_length=run.target_min_length,
            target_max_length=run.target_max_length,
            target_tone=run.target_tone,
            provider=run.provider,
            model=run.model,
            prompt_version=run.prompt_version,
            schema_version=run.schema_version,
            input_hash=run.input_hash,
            source_hash=run.source_hash,
            outdated=run.outdated,
            started_at=run.started_at,
            completed_at=run.completed_at,
            error_code=run.error_code,
            safe_error_message=run.safe_error_message,
            overall_feedback=run.overall_feedback,
            suggested_title=run.suggested_title,
            suggested_content=run.suggested_content,
            warnings=run.warnings or [],
            missing_information=run.missing_information or [],
            confidence=run.confidence or {},
            usage_metadata=run.usage_metadata or {},
            created_at=run.created_at,
            updated_at=run.updated_at,
            suggestions=[DocumentImprovementSuggestionPublic.model_validate(item) for item in run.suggestions],
            sources=[DocumentImprovementSourcePublic.model_validate(source) for source in run.sources],
            actions=[DocumentImprovementActionPublic.model_validate(action) for action in run.actions],
        )


def _hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()
