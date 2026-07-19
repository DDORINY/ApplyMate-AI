from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError
from app.models.application import (
    Application,
    ApplicationNote,
    ApplicationStatus,
    ApplicationStatusHistory,
    ApplicationStatusHistorySource,
)
from app.models.application_document import ApplicationDocument, ApplicationDocumentVersion
from app.models.job import JobAnalysis, JobMatch, JobPosting
from app.models.resume import Resume, ResumeAnalysis, ResumeFile
from app.repositories.application import ApplicationRepository
from app.schemas.application import (
    ApplicationCreate,
    ApplicationListData,
    ApplicationNoteCreate,
    ApplicationNotePublic,
    ApplicationNoteUpdate,
    ApplicationOptionsData,
    ApplicationOptionItem,
    ApplicationPublic,
    ApplicationStatusChange,
    ApplicationStatusHistoryPublic,
    ApplicationUpdate,
)


class ApplicationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ApplicationRepository(session)

    async def create_application(self, user_id: int, payload: ApplicationCreate) -> Application:
        links = await self._validate_links(user_id, payload.model_dump())
        job = links["job"]
        application = Application(
            user_id=user_id,
            job_id=links["job_id"],
            resume_id=links["resume_id"],
            resume_file_id=links["resume_file_id"],
            application_document_id=links["application_document_id"],
            application_document_version_id=links["application_document_version_id"],
            status=payload.status,
            applied_at=payload.applied_at,
            planned_apply_at=payload.planned_apply_at,
            application_channel=payload.application_channel,
            application_url=payload.application_url,
            contact_name=payload.contact_name,
            contact_email=str(payload.contact_email) if payload.contact_email else None,
            contact_phone=payload.contact_phone,
            source=payload.source,
            priority=payload.priority,
            result_announced_at=payload.result_announced_at,
            closed_at=payload.closed_at,
            company_name_snapshot=job.company.name if job and job.company else None,
            job_title_snapshot=job.title if job else None,
            job_url_snapshot=job.source_url if job else payload.application_url,
        )
        self.session.add(application)
        await self.session.flush()
        self.session.add(
            ApplicationStatusHistory(
                application_id=application.id,
                user_id=user_id,
                previous_status=None,
                new_status=payload.status,
                changed_at=datetime.now(UTC),
                reason="initial_status",
                source=ApplicationStatusHistorySource.USER,
            )
        )
        await self.session.commit()
        return await self._get_application_or_404(user_id, application.id)

    async def list_applications(self, user_id: int, **filters) -> ApplicationListData:
        page = filters.pop("page")
        size = filters.pop("size")
        applications, total = await self.repository.list_applications(user_id, page=page, size=size, **filters)
        total_pages = (total + size - 1) // size if total else 0
        return ApplicationListData(
            items=[self._to_public(application) for application in applications],
            page=page,
            size=size,
            total=total,
            total_pages=total_pages,
        )

    async def get_application(self, user_id: int, application_id: int) -> Application:
        return await self._get_application_or_404(user_id, application_id)

    async def update_application(
        self, user_id: int, application_id: int, payload: ApplicationUpdate
    ) -> Application:
        application = await self._get_application_or_404(user_id, application_id)
        data = payload.model_dump(exclude_unset=True)
        link_fields = {
            "job_id": application.job_id,
            "resume_id": application.resume_id,
            "resume_file_id": application.resume_file_id,
            "application_document_id": application.application_document_id,
            "application_document_version_id": application.application_document_version_id,
        }
        link_fields.update({key: data[key] for key in link_fields if key in data})
        links = await self._validate_links(user_id, link_fields)
        job = links["job"]
        for field, value in data.items():
            if field == "contact_email" and value is not None:
                value = str(value)
            setattr(application, field, value)
        application.job_id = links["job_id"]
        application.resume_id = links["resume_id"]
        application.resume_file_id = links["resume_file_id"]
        application.application_document_id = links["application_document_id"]
        application.application_document_version_id = links["application_document_version_id"]
        if job:
            application.company_name_snapshot = job.company.name if job.company else None
            application.job_title_snapshot = job.title
            application.job_url_snapshot = job.source_url
        await self.session.commit()
        return await self._get_application_or_404(user_id, application_id)

    async def archive_application(self, user_id: int, application_id: int) -> dict[str, bool]:
        application = await self._get_application_or_404(user_id, application_id)
        application.is_archived = True
        application.archived_at = datetime.now(UTC)
        await self.session.commit()
        return {"archived": True}

    async def change_status(
        self, user_id: int, application_id: int, payload: ApplicationStatusChange
    ) -> Application:
        application = await self._get_application_or_404(user_id, application_id)
        previous = application.status
        changed_at = payload.changed_at or datetime.now(UTC)
        application.status = payload.status
        if payload.status == ApplicationStatus.CLOSED and application.closed_at is None:
            application.closed_at = changed_at
        self.session.add(
            ApplicationStatusHistory(
                application_id=application.id,
                user_id=user_id,
                previous_status=previous,
                new_status=payload.status,
                changed_at=changed_at,
                reason=payload.reason,
                note=payload.note,
                source=payload.source,
            )
        )
        await self.session.commit()
        return await self._get_application_or_404(user_id, application_id)

    async def list_status_history(
        self, user_id: int, application_id: int
    ) -> list[ApplicationStatusHistoryPublic]:
        await self._get_application_or_404(user_id, application_id, include_archived=True)
        history = await self.repository.list_status_history(user_id, application_id)
        return [ApplicationStatusHistoryPublic.model_validate(item) for item in history]

    async def create_note(
        self, user_id: int, application_id: int, payload: ApplicationNoteCreate
    ) -> ApplicationNote:
        await self._get_application_or_404(user_id, application_id)
        note = ApplicationNote(
            application_id=application_id,
            user_id=user_id,
            content=payload.content,
            note_type=payload.note_type,
            is_pinned=payload.is_pinned,
        )
        self.session.add(note)
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def list_notes(self, user_id: int, application_id: int) -> list[ApplicationNotePublic]:
        await self._get_application_or_404(user_id, application_id, include_archived=True)
        notes = await self.repository.list_notes(user_id, application_id)
        return [ApplicationNotePublic.model_validate(note) for note in notes]

    async def update_note(
        self, user_id: int, application_id: int, note_id: int, payload: ApplicationNoteUpdate
    ) -> ApplicationNote:
        await self._get_application_or_404(user_id, application_id, include_archived=True)
        note = await self.repository.get_note(user_id, application_id, note_id)
        if not note:
            raise AppError("APPLICATION_NOTE_NOT_FOUND", "Application note was not found.", 404)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(note, field, value)
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def delete_note(self, user_id: int, application_id: int, note_id: int) -> dict[str, bool]:
        await self._get_application_or_404(user_id, application_id, include_archived=True)
        note = await self.repository.get_note(user_id, application_id, note_id)
        if not note:
            raise AppError("APPLICATION_NOTE_NOT_FOUND", "Application note was not found.", 404)
        await self.session.delete(note)
        await self.session.commit()
        return {"deleted": True}

    async def options(self, user_id: int) -> ApplicationOptionsData:
        jobs = (
            await self.session.execute(
                select(JobPosting).options(selectinload(JobPosting.company)).where(JobPosting.user_id == user_id).order_by(JobPosting.updated_at.desc())
            )
        ).scalars().all()
        resumes = (await self.session.execute(select(Resume).where(Resume.user_id == user_id).order_by(Resume.updated_at.desc()))).scalars().all()
        files = (await self.session.execute(select(ResumeFile).where(ResumeFile.user_id == user_id).order_by(ResumeFile.created_at.desc()))).scalars().all()
        resume_analyses = (await self.session.execute(select(ResumeAnalysis).where(ResumeAnalysis.user_id == user_id).order_by(ResumeAnalysis.updated_at.desc()))).scalars().all()
        job_analyses = (await self.session.execute(select(JobAnalysis).where(JobAnalysis.user_id == user_id).order_by(JobAnalysis.updated_at.desc()))).scalars().all()
        matches = (await self.session.execute(select(JobMatch).where(JobMatch.user_id == user_id).order_by(JobMatch.updated_at.desc()))).scalars().all()
        documents = (
            await self.session.execute(
                select(ApplicationDocument).where(ApplicationDocument.user_id == user_id, ApplicationDocument.is_archived.is_(False)).order_by(ApplicationDocument.updated_at.desc())
            )
        ).scalars().all()
        versions = (
            await self.session.execute(
                select(ApplicationDocumentVersion).where(ApplicationDocumentVersion.user_id == user_id).order_by(ApplicationDocumentVersion.created_at.desc())
            )
        ).scalars().all()
        return ApplicationOptionsData(
            jobs=[
                ApplicationOptionItem(
                    id=job.id,
                    label=f"{job.company.name if job.company else 'Unknown'} · {job.title}",
                    description=job.position or job.source_url,
                    metadata={"company_name": job.company.name if job.company else None, "source_url": job.source_url},
                )
                for job in jobs
            ],
            resumes=[ApplicationOptionItem(id=resume.id, label=resume.title, description=resume.description) for resume in resumes],
            resume_files=[
                ApplicationOptionItem(id=file.id, label=file.original_filename, description=f"resume #{file.resume_id}", metadata={"resume_id": file.resume_id})
                for file in files
            ],
            resume_analyses=[
                ApplicationOptionItem(id=item.id, label=f"이력서 분석 #{item.id}", description=item.summary, metadata={"resume_id": item.resume_id, "resume_file_id": item.resume_file_id, "status": item.status.value})
                for item in resume_analyses
            ],
            job_analyses=[
                ApplicationOptionItem(id=item.id, label=f"공고 분석 #{item.id}", description=item.summary, metadata={"job_id": item.job_posting_id, "status": item.status.value})
                for item in job_analyses
            ],
            job_matches=[
                ApplicationOptionItem(id=item.id, label=f"적합도 #{item.id} · {item.grade.value}", description=item.recommendation_summary, metadata={"job_id": item.job_posting_id, "score": item.total_score})
                for item in matches
            ],
            application_documents=[
                ApplicationOptionItem(id=doc.id, label=doc.title, description=doc.document_type.value, metadata={"job_id": doc.job_id, "resume_id": doc.resume_id, "current_version_number": doc.current_version_number})
                for doc in documents
            ],
            application_document_versions=[
                ApplicationOptionItem(id=version.id, label=f"문서 #{version.document_id} v{version.version_number}", description=version.content[:120], metadata={"document_id": version.document_id, "version_number": version.version_number, "character_count": version.character_count})
                for version in versions
            ],
        )

    async def _get_application_or_404(
        self, user_id: int, application_id: int, *, include_archived: bool = False
    ) -> Application:
        application = await self.repository.get_application(
            user_id, application_id, include_archived=include_archived
        )
        if not application:
            raise AppError("APPLICATION_NOT_FOUND", "Application was not found.", 404)
        return application

    async def _validate_links(self, user_id: int, data: dict) -> dict[str, object]:
        job = await self._get_owned(JobPosting, user_id, data.get("job_id"), "JOB_NOT_FOUND", load_company=True)
        resume = await self._get_owned(Resume, user_id, data.get("resume_id"), "RESUME_NOT_FOUND")
        resume_file = await self._get_owned(ResumeFile, user_id, data.get("resume_file_id"), "RESUME_FILE_NOT_FOUND")
        document = await self._get_owned(ApplicationDocument, user_id, data.get("application_document_id"), "DOCUMENT_NOT_FOUND")
        version = await self._get_owned(
            ApplicationDocumentVersion,
            user_id,
            data.get("application_document_version_id"),
            "DOCUMENT_VERSION_NOT_FOUND",
        )

        resume_id = data.get("resume_id")
        if resume_file:
            if resume_id and resume_file.resume_id != resume_id:
                raise AppError("APPLICATION_INVALID_RELATION", "Resume file does not belong to the selected resume.", 400)
            resume_id = resume_file.resume_id
        document_id = data.get("application_document_id")
        if version:
            if document_id and version.document_id != document_id:
                raise AppError("APPLICATION_INVALID_RELATION", "Document version does not belong to the selected document.", 400)
            document_id = version.document_id
            if document is None:
                document = await self._get_owned(ApplicationDocument, user_id, document_id, "DOCUMENT_NOT_FOUND")
        if document:
            if job and document.job_id and document.job_id != job.id:
                raise AppError("APPLICATION_INVALID_RELATION", "Document is linked to a different job posting.", 400)
            if resume_id and document.resume_id and document.resume_id != resume_id:
                raise AppError("APPLICATION_INVALID_RELATION", "Document is linked to a different resume.", 400)
            if document.job_id and not data.get("job_id"):
                job = await self._get_owned(JobPosting, user_id, document.job_id, "JOB_NOT_FOUND", load_company=True)
                data["job_id"] = document.job_id
            if document.resume_id and not resume_id:
                resume_id = document.resume_id
        if resume and resume_id and resume.id != resume_id:
            raise AppError("APPLICATION_INVALID_RELATION", "Selected resume relation is invalid.", 400)
        return {
            "job": job,
            "job_id": data.get("job_id"),
            "resume_id": resume_id,
            "resume_file_id": data.get("resume_file_id"),
            "application_document_id": document_id,
            "application_document_version_id": data.get("application_document_version_id"),
        }

    async def _get_owned(self, model, user_id: int, item_id: int | None, code: str, *, load_company: bool = False):
        if not item_id:
            return None
        query = select(model).where(model.id == item_id, model.user_id == user_id)
        if load_company:
            query = query.options(selectinload(model.company))
        item = await self.session.scalar(query)
        if not item:
            raise AppError(code, "Linked resource was not found.", 404)
        return item

    def _to_public(self, application: Application) -> ApplicationPublic:
        public = ApplicationPublic.model_validate(application)
        public.notes_count = len(application.notes or [])
        return public
