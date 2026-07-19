import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.application_document_prompt import (
    APPLICATION_DOCUMENT_PROMPT_VERSION,
    APPLICATION_DOCUMENT_SCHEMA_VERSION,
    SYSTEM_PROMPT,
    build_application_document_prompt,
)
from app.ai.providers import get_ai_provider, provider_status
from app.core.config import settings
from app.core.exceptions import AppError
from app.models.application_document import (
    ApplicationDocument,
    ApplicationDocumentSource,
    ApplicationDocumentStatus,
    ApplicationDocumentType,
    ApplicationDocumentVersion,
    GenerationRun,
    GenerationRunStatus,
)
from app.models.career import CareerProfile, Experience, Project, UserSkill
from app.models.job import JobAnalysis, JobMatch, JobPosting
from app.models.resume import Resume, ResumeAnalysis, ResumeFile, ResumeFileExtraction
from app.repositories.application_document import ApplicationDocumentRepository
from app.schemas.application_document import (
    ApplicationDocumentCreate,
    ApplicationDocumentDuplicateRequest,
    ApplicationDocumentGenerateRequest,
    ApplicationDocumentListData,
    ApplicationDocumentPublic,
    ApplicationDocumentStructuredData,
    ApplicationDocumentUpdate,
    ApplicationDocumentVersionCreate,
    ApplicationDocumentVersionPublic,
    DocumentProviderStatus,
)


class ApplicationDocumentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ApplicationDocumentRepository(session)

    async def create_document(self, user_id: int, payload: ApplicationDocumentCreate) -> ApplicationDocument:
        await self._validate_linked_sources(user_id, payload)
        document = ApplicationDocument(
            user_id=user_id,
            job_id=payload.job_id,
            resume_id=payload.resume_id,
            resume_file_id=payload.resume_file_id,
            resume_analysis_id=payload.resume_analysis_id,
            job_analysis_id=payload.job_analysis_id,
            job_match_id=payload.job_match_id,
            document_type=payload.document_type,
            title=payload.title.strip(),
            question=payload.question,
            instructions=payload.instructions,
            tone=payload.tone,
            language=payload.language,
            character_limit=payload.character_limit,
            minimum_character_count=payload.minimum_character_count,
            target_character_count=payload.target_character_count,
            maximum_character_count=payload.maximum_character_count,
            focus_points=payload.focus_points,
            avoid_phrases=payload.avoid_phrases,
            settings=payload.settings,
        )
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def list_documents(
        self,
        user_id: int,
        *,
        page: int,
        size: int,
        document_type: ApplicationDocumentType | None,
        status: ApplicationDocumentStatus | None,
        job_id: int | None,
        resume_id: int | None,
        keyword: str | None,
        include_archived: bool,
    ) -> ApplicationDocumentListData:
        documents, total = await self.repository.list_documents(
            user_id,
            page=page,
            size=size,
            document_type=document_type,
            status=status,
            job_id=job_id,
            resume_id=resume_id,
            keyword=keyword,
            include_archived=include_archived,
        )
        return ApplicationDocumentListData(
            items=[self._to_public(document) for document in documents],
            total=total,
            page=page,
            size=size,
        )

    async def get_document(self, user_id: int, document_id: int) -> ApplicationDocument:
        return await self._get_document_or_404(user_id, document_id)

    async def update_document(
        self, user_id: int, document_id: int, payload: ApplicationDocumentUpdate
    ) -> ApplicationDocument:
        document = await self._get_document_or_404(user_id, document_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(document, field, value)
        await self.session.commit()
        await self.session.refresh(document)
        return await self._get_document_or_404(user_id, document_id)

    async def archive_document(self, user_id: int, document_id: int) -> dict[str, bool]:
        document = await self._get_document_or_404(user_id, document_id)
        document.is_archived = True
        document.status = ApplicationDocumentStatus.ARCHIVED
        await self.session.commit()
        return {"archived": True}

    async def generate(
        self,
        user_id: int,
        document_id: int,
        payload: ApplicationDocumentGenerateRequest | None = None,
    ) -> ApplicationDocument:
        document = await self._get_document_or_404(user_id, document_id)
        payload = payload or ApplicationDocumentGenerateRequest()
        original = {
            "question": document.question,
            "instructions": document.instructions,
            "character_limit": document.character_limit,
            "tone": document.tone,
            "focus_points": document.focus_points,
        }
        if payload.question is not None:
            document.question = payload.question
        if payload.instructions is not None:
            document.instructions = payload.instructions
        if payload.character_limit is not None:
            document.character_limit = payload.character_limit
        if payload.tone is not None:
            document.tone = payload.tone
        if payload.focus_points is not None:
            document.focus_points = [item.strip() for item in payload.focus_points if item.strip()]

        source_records = await self._build_sources(document)
        prompt = build_application_document_prompt(
            title=document.title,
            document_type=document.document_type,
            question=document.question,
            instructions=document.instructions,
            tone=document.tone.value,
            language=document.language,
            character_limit=document.character_limit,
            focus_points=document.focus_points,
            sources=source_records,
        )
        input_hash = _hash({"document_id": document.id, "prompt": prompt})
        provider = get_ai_provider(settings)
        run = GenerationRun(
            document_id=document.id,
            user_id=user_id,
            status=GenerationRunStatus.PROCESSING,
            provider=provider.provider,
            model=provider.model,
            prompt_version=APPLICATION_DOCUMENT_PROMPT_VERSION,
            schema_version=APPLICATION_DOCUMENT_SCHEMA_VERSION,
            input_hash=input_hash,
            settings={
                "document_type": document.document_type.value,
                "tone": document.tone.value,
                "language": document.language,
                "character_limit": document.character_limit,
            },
            started_at=datetime.now(UTC),
            usage_metadata={},
        )
        self.session.add(run)
        document.status = ApplicationDocumentStatus.GENERATING
        await self.session.flush()
        try:
            result = await provider.generate_application_document(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=prompt,
                response_schema=ApplicationDocumentStructuredData,
            )
            data = result.parsed_data
            if not isinstance(data, ApplicationDocumentStructuredData):
                data = ApplicationDocumentStructuredData.model_validate(data.model_dump())
            validation_warnings = self._validate_blocks(data, source_records)
            counts = _content_counts(data.content, document.character_limit or document.maximum_character_count)
            next_number = await self.repository.latest_version_number(document.id) + 1
            version = ApplicationDocumentVersion(
                document_id=document.id,
                user_id=user_id,
                version_number=next_number,
                content=data.content,
                content_blocks=[block.model_dump() for block in data.blocks],
                is_ai_generated=True,
                is_user_edited=False,
                generation_run_id=run.id,
                change_summary="AI generated draft",
                **counts,
            )
            self.session.add(version)
            await self.session.flush()
            self._store_source_snapshots(document, version, source_records, data)
            review_required = data.requires_review or bool(validation_warnings) or counts["limit_exceeded"]
            document.status = (
                ApplicationDocumentStatus.REVIEW_REQUIRED if review_required else ApplicationDocumentStatus.COMPLETED
            )
            document.current_version_number = next_number
            run.status = GenerationRunStatus.COMPLETED
            run.model = result.model
            run.completed_at = datetime.now(UTC)
            run.usage_metadata = {
                "request_id": result.request_id,
                "prompt_tokens": result.prompt_tokens,
                "completion_tokens": result.completion_tokens,
                "total_tokens": result.total_tokens,
                "latency_ms": result.latency_ms,
            }
            run.result_snapshot = {
                "title": data.title,
                "warnings": [*data.warnings, *validation_warnings],
                "requires_review": review_required,
            }
            await self.session.commit()
        except AppError as exc:
            run.status = (
                GenerationRunStatus.PROVIDER_UNAVAILABLE
                if exc.code.startswith("AI_PROVIDER")
                else GenerationRunStatus.FAILED
            )
            run.error_code = exc.code
            run.safe_error_message = exc.message[:500]
            run.completed_at = datetime.now(UTC)
            document.status = ApplicationDocumentStatus.FAILED
            for key, value in original.items():
                setattr(document, key, value)
            await self.session.commit()
            raise
        return await self._get_document_or_404(user_id, document_id)

    async def create_user_version(
        self, user_id: int, document_id: int, payload: ApplicationDocumentVersionCreate
    ) -> ApplicationDocumentVersion:
        document = await self._get_document_or_404(user_id, document_id)
        next_number = await self.repository.latest_version_number(document.id) + 1
        blocks = [block.model_dump() for block in payload.content_blocks] if payload.content_blocks else []
        version = ApplicationDocumentVersion(
            document_id=document.id,
            user_id=user_id,
            version_number=next_number,
            content=payload.content,
            content_blocks=blocks,
            is_ai_generated=False,
            is_user_edited=True,
            change_summary=payload.change_summary,
            **_content_counts(payload.content, document.character_limit or document.maximum_character_count),
        )
        self.session.add(version)
        await self.session.flush()
        document.current_version_number = next_number
        document.status = ApplicationDocumentStatus.REVIEW_REQUIRED if version.limit_exceeded else ApplicationDocumentStatus.COMPLETED
        await self.session.commit()
        await self.session.refresh(version)
        return version

    async def restore_version(
        self, user_id: int, document_id: int, version_id: int
    ) -> ApplicationDocumentVersion:
        document = await self._get_document_or_404(user_id, document_id)
        source_version = await self.repository.get_version(user_id, document_id, version_id)
        if not source_version:
            raise AppError("DOCUMENT_VERSION_NOT_FOUND", "Document version was not found.", 404)
        next_number = await self.repository.latest_version_number(document.id) + 1
        restored = ApplicationDocumentVersion(
            document_id=document.id,
            user_id=user_id,
            version_number=next_number,
            content=source_version.content,
            content_blocks=source_version.content_blocks,
            is_ai_generated=False,
            is_user_edited=True,
            change_summary=f"Restored from version {source_version.version_number}",
            **_content_counts(source_version.content, document.character_limit or document.maximum_character_count),
        )
        self.session.add(restored)
        await self.session.flush()
        document.current_version_number = next_number
        document.status = ApplicationDocumentStatus.REVIEW_REQUIRED if restored.limit_exceeded else ApplicationDocumentStatus.COMPLETED
        await self.session.commit()
        await self.session.refresh(restored)
        return restored

    async def duplicate_document(
        self, user_id: int, document_id: int, payload: ApplicationDocumentDuplicateRequest
    ) -> ApplicationDocument:
        source = await self._get_document_or_404(user_id, document_id)
        current = self._current_version(source)
        duplicate = ApplicationDocument(
            user_id=user_id,
            job_id=source.job_id,
            resume_id=source.resume_id,
            resume_file_id=source.resume_file_id,
            resume_analysis_id=source.resume_analysis_id,
            job_analysis_id=source.job_analysis_id,
            job_match_id=source.job_match_id,
            document_type=source.document_type,
            title=payload.title or f"{source.title} 복사본",
            question=source.question,
            instructions=source.instructions,
            tone=source.tone,
            language=source.language,
            character_limit=source.character_limit,
            minimum_character_count=source.minimum_character_count,
            target_character_count=source.target_character_count,
            maximum_character_count=source.maximum_character_count,
            focus_points=source.focus_points,
            avoid_phrases=source.avoid_phrases,
            settings={**source.settings, "duplicated_from_document_id": source.id},
            status=source.status if current else ApplicationDocumentStatus.DRAFT,
            current_version_number=1 if current else None,
        )
        self.session.add(duplicate)
        await self.session.flush()
        if current:
            version = ApplicationDocumentVersion(
                document_id=duplicate.id,
                user_id=user_id,
                version_number=1,
                content=current.content,
                content_blocks=current.content_blocks,
                is_ai_generated=current.is_ai_generated,
                is_user_edited=current.is_user_edited,
                change_summary=f"Duplicated from document {source.id}",
                **_content_counts(current.content, duplicate.character_limit or duplicate.maximum_character_count),
            )
            self.session.add(version)
            await self.session.flush()
            for source_row in await self.repository.list_sources(user_id, source.id, current.id):
                self.session.add(
                    ApplicationDocumentSource(
                        document_id=duplicate.id,
                        version_id=version.id,
                        user_id=user_id,
                        source_type=source_row.source_type,
                        source_id=source_row.source_id,
                        source_version=source_row.source_version,
                        source_hash=source_row.source_hash,
                        field_path=source_row.field_path,
                        source_snapshot=source_row.source_snapshot,
                        evidence=source_row.evidence,
                    )
                )
        await self.session.commit()
        return await self._get_document_or_404(user_id, duplicate.id)

    async def list_versions(self, user_id: int, document_id: int) -> list[ApplicationDocumentVersion]:
        await self._get_document_or_404(user_id, document_id)
        return await self.repository.list_versions(user_id, document_id)

    async def get_version(
        self, user_id: int, document_id: int, version_id: int
    ) -> ApplicationDocumentVersion:
        await self._get_document_or_404(user_id, document_id)
        version = await self.repository.get_version(user_id, document_id, version_id)
        if not version:
            raise AppError("DOCUMENT_VERSION_NOT_FOUND", "Document version was not found.", 404)
        return version

    async def list_sources(
        self, user_id: int, document_id: int, version_id: int | None = None
    ) -> list[ApplicationDocumentSource]:
        await self._get_document_or_404(user_id, document_id)
        return await self.repository.list_sources(user_id, document_id, version_id)

    async def list_generation_runs(self, user_id: int, document_id: int) -> list[GenerationRun]:
        await self._get_document_or_404(user_id, document_id)
        return await self.repository.list_generation_runs(user_id, document_id)

    async def get_generation_run(self, user_id: int, document_id: int, run_id: int) -> GenerationRun:
        await self._get_document_or_404(user_id, document_id)
        run = await self.repository.get_generation_run(user_id, document_id, run_id)
        if not run:
            raise AppError("DOCUMENT_GENERATION_RUN_NOT_FOUND", "Generation run was not found.", 404)
        return run

    def provider_status(self) -> DocumentProviderStatus:
        status = provider_status(settings)
        return DocumentProviderStatus(
            active_provider=str(status["active_provider"]),
            enabled=bool(status["enabled"]),
            model=status["model"] if isinstance(status["model"], str) or status["model"] is None else None,
            generation_available=bool(status.get("generation_available", status["analysis_available"])),
        )

    async def _get_document_or_404(self, user_id: int, document_id: int) -> ApplicationDocument:
        document = await self.repository.get_document(user_id, document_id)
        if not document:
            raise AppError("DOCUMENT_NOT_FOUND", "Document was not found.", 404)
        return document

    async def _validate_linked_sources(self, user_id: int, payload: ApplicationDocumentCreate) -> None:
        checks = [
            (payload.job_id, JobPosting, "JOB_NOT_FOUND"),
            (payload.resume_id, Resume, "RESUME_NOT_FOUND"),
            (payload.resume_file_id, ResumeFile, "RESUME_FILE_NOT_FOUND"),
            (payload.resume_analysis_id, ResumeAnalysis, "RESUME_ANALYSIS_NOT_FOUND"),
            (payload.job_analysis_id, JobAnalysis, "JOB_ANALYSIS_NOT_FOUND"),
            (payload.job_match_id, JobMatch, "JOB_MATCH_NOT_FOUND"),
        ]
        for source_id, model, code in checks:
            if not source_id:
                continue
            result = await self.session.execute(select(model).where(model.id == source_id, model.user_id == user_id))
            if not result.scalar_one_or_none():
                raise AppError(code, "Linked source was not found.", 404)

    async def _build_sources(self, document: ApplicationDocument) -> list[dict[str, object]]:
        sources: list[dict[str, object]] = []
        if document.question:
            sources.append(_source("user_question", "manual", "question", document.question))
        if document.instructions:
            sources.append(_source("user_instruction", "manual", "instructions", document.instructions))

        profile = await self.session.scalar(select(CareerProfile).where(CareerProfile.user_id == document.user_id))
        if profile:
            sources.append(_source("career_profile", profile.id, "summary", f"{profile.display_name} {profile.headline or ''} {profile.desired_job_title} {profile.introduction or ''}"))
        skill_result = await self.session.execute(select(UserSkill).where(UserSkill.user_id == document.user_id))
        skills = [str(skill.skill_id) for skill in skill_result.scalars().all()]
        if skills:
            sources.append(_source("career_profile", "skills", "skills", "사용자 등록 기술 ID: " + ", ".join(skills)))
        experience_result = await self.session.execute(select(Experience).where(Experience.user_id == document.user_id).order_by(Experience.start_date.desc()))
        for experience in experience_result.scalars().all()[:3]:
            sources.append(_source("career_experience", experience.id, "description", f"{experience.company_name} {experience.position} {experience.description or ''} {experience.achievements or ''}"))
        project_result = await self.session.execute(select(Project).where(Project.user_id == document.user_id).order_by(Project.start_date.desc()))
        for project in project_result.scalars().all()[:3]:
            sources.append(_source("project", project.id, "description", f"{project.name} {project.summary or ''} {project.role or ''} {project.description or ''} {project.achievements or ''}"))
        if document.job_id:
            job = await self.session.scalar(select(JobPosting).where(JobPosting.id == document.job_id, JobPosting.user_id == document.user_id))
            if job:
                sources.append(_source("job_posting", job.id, "description", f"{job.title} {job.position or ''} {job.description or ''} {job.requirements or ''} {job.preferred_qualifications or ''}"))
        if document.job_analysis_id:
            analysis = await self.session.scalar(select(JobAnalysis).where(JobAnalysis.id == document.job_analysis_id, JobAnalysis.user_id == document.user_id))
            if analysis:
                sources.append(_source("job_analysis", analysis.id, "summary", f"{analysis.summary or ''} {json.dumps(analysis.technical_skills or [], ensure_ascii=False)} {json.dumps(analysis.required_qualifications or [], ensure_ascii=False)}"))
        if document.job_match_id:
            match = await self.session.scalar(select(JobMatch).where(JobMatch.id == document.job_match_id, JobMatch.user_id == document.user_id))
            if match:
                sources.append(_source("job_match", match.id, "recommendation_summary", f"{match.recommendation_summary or ''} {json.dumps(match.strengths or [], ensure_ascii=False)} {json.dumps(match.gaps or [], ensure_ascii=False)}"))
        if document.resume_file_id:
            extraction = await self.session.scalar(select(ResumeFileExtraction).where(ResumeFileExtraction.resume_file_id == document.resume_file_id, ResumeFileExtraction.user_id == document.user_id))
            if extraction and extraction.extracted_text:
                sources.append(_source("resume_extraction", extraction.id, "extracted_text", extraction.extracted_text[:2000]))
        if document.resume_analysis_id:
            resume_analysis = await self.session.scalar(select(ResumeAnalysis).where(ResumeAnalysis.id == document.resume_analysis_id, ResumeAnalysis.user_id == document.user_id))
            if resume_analysis:
                sources.append(_source("resume_analysis", resume_analysis.id, "result", f"{resume_analysis.summary or ''} {json.dumps(resume_analysis.result or {}, ensure_ascii=False)[:2000]}"))
        return [source for source in sources if str(source.get("text") or "").strip()]

    def _validate_blocks(
        self, data: ApplicationDocumentStructuredData, sources: list[dict[str, object]]
    ) -> list[str]:
        valid_keys = {(str(source["source_type"]), str(source["source_id"])) for source in sources}
        warnings: list[str] = []
        for block in data.blocks:
            if not block.source_references:
                warnings.append(f"BLOCK_{block.sequence}_SOURCE_MISSING")
                continue
            for reference in block.source_references:
                if (reference.source_type, reference.source_id) not in valid_keys:
                    warnings.append(f"BLOCK_{block.sequence}_SOURCE_INVALID")
                if not reference.evidence_text.strip():
                    warnings.append(f"BLOCK_{block.sequence}_EVIDENCE_EMPTY")
        return warnings

    def _store_source_snapshots(
        self,
        document: ApplicationDocument,
        version: ApplicationDocumentVersion,
        sources: list[dict[str, object]],
        data: ApplicationDocumentStructuredData,
    ) -> None:
        source_map = {(str(source["source_type"]), str(source["source_id"])): source for source in sources}
        seen: set[tuple[str, str, str | None]] = set()
        for block in data.blocks:
            for reference in block.source_references:
                key = (reference.source_type, reference.source_id, reference.field_path)
                if key in seen:
                    continue
                seen.add(key)
                source = source_map.get((reference.source_type, reference.source_id))
                if not source:
                    continue
                self.session.add(
                    ApplicationDocumentSource(
                        document_id=document.id,
                        version_id=version.id,
                        user_id=document.user_id,
                        source_type=reference.source_type,
                        source_id=reference.source_id,
                        source_version=str(source.get("source_version") or "current"),
                        source_hash=str(source["source_hash"]),
                        field_path=reference.field_path,
                        source_snapshot={
                            "text": str(source.get("text") or "")[:2000],
                            "field_path": reference.field_path,
                        },
                        evidence=reference.model_dump(),
                    )
                )

    def _to_public(self, document: ApplicationDocument) -> ApplicationDocumentPublic:
        public = ApplicationDocumentPublic.model_validate(document)
        current = self._current_version(document)
        public.current_version = (
            ApplicationDocumentVersionPublic.model_validate(current) if current else None
        )
        return public

    def _current_version(self, document: ApplicationDocument) -> ApplicationDocumentVersion | None:
        if not document.current_version_number:
            return None
        for version in document.versions:
            if version.version_number == document.current_version_number:
                return version
        return None


def _source(source_type: str, source_id: int | str, field_path: str, text: str) -> dict[str, object]:
    return {
        "source_type": source_type,
        "source_id": str(source_id),
        "field_path": field_path,
        "text": text,
        "source_hash": _hash({"source_type": source_type, "source_id": str(source_id), "field_path": field_path, "text": text}),
        "source_version": "current",
    }


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def _content_counts(content: str, limit: int | None) -> dict[str, int | bool]:
    paragraphs = [part for part in content.split("\n\n") if part.strip()]
    return {
        "character_count": len(content),
        "character_count_without_spaces": len("".join(content.split())),
        "word_count": len(content.split()),
        "paragraph_count": len(paragraphs) or (1 if content.strip() else 0),
        "limit_exceeded": bool(limit and len(content) > limit),
    }
