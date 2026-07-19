from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application_document import (
    ApplicationDocument,
    ApplicationDocumentSource,
    ApplicationDocumentStatus,
    ApplicationDocumentType,
    ApplicationDocumentVersion,
    GenerationRun,
)


class ApplicationDocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_documents(
        self,
        user_id: int,
        *,
        page: int,
        size: int,
        document_type: ApplicationDocumentType | None = None,
        status: ApplicationDocumentStatus | None = None,
        job_id: int | None = None,
        resume_id: int | None = None,
        keyword: str | None = None,
        include_archived: bool = False,
    ) -> tuple[list[ApplicationDocument], int]:
        query = select(ApplicationDocument).where(ApplicationDocument.user_id == user_id)
        if not include_archived:
            query = query.where(ApplicationDocument.is_archived.is_(False))
        query = self._apply_filters(
            query,
            document_type=document_type,
            status=status,
            job_id=job_id,
            resume_id=resume_id,
            keyword=keyword,
        )
        total_result = await self.session.execute(
            select(func.count()).select_from(query.order_by(None).subquery())
        )
        total = int(total_result.scalar_one())
        result = await self.session.execute(
            query.options(selectinload(ApplicationDocument.versions))
            .order_by(ApplicationDocument.updated_at.desc(), ApplicationDocument.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().all()), total

    async def get_document(
        self, user_id: int, document_id: int, *, include_archived: bool = False
    ) -> ApplicationDocument | None:
        query = (
            select(ApplicationDocument)
            .options(selectinload(ApplicationDocument.versions))
            .where(ApplicationDocument.id == document_id, ApplicationDocument.user_id == user_id)
            .execution_options(populate_existing=True)
        )
        if not include_archived:
            query = query.where(ApplicationDocument.is_archived.is_(False))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_version(
        self, user_id: int, document_id: int, version_id: int
    ) -> ApplicationDocumentVersion | None:
        result = await self.session.execute(
            select(ApplicationDocumentVersion).where(
                ApplicationDocumentVersion.id == version_id,
                ApplicationDocumentVersion.document_id == document_id,
                ApplicationDocumentVersion.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_versions(self, user_id: int, document_id: int) -> list[ApplicationDocumentVersion]:
        result = await self.session.execute(
            select(ApplicationDocumentVersion)
            .where(
                ApplicationDocumentVersion.document_id == document_id,
                ApplicationDocumentVersion.user_id == user_id,
            )
            .order_by(ApplicationDocumentVersion.version_number.desc())
        )
        return list(result.scalars().all())

    async def latest_version_number(self, document_id: int) -> int:
        result = await self.session.execute(
            select(func.coalesce(func.max(ApplicationDocumentVersion.version_number), 0)).where(
                ApplicationDocumentVersion.document_id == document_id
            )
        )
        return int(result.scalar_one())

    async def list_sources(
        self, user_id: int, document_id: int, version_id: int | None = None
    ) -> list[ApplicationDocumentSource]:
        query = select(ApplicationDocumentSource).where(
            ApplicationDocumentSource.document_id == document_id,
            ApplicationDocumentSource.user_id == user_id,
        )
        if version_id:
            query = query.where(ApplicationDocumentSource.version_id == version_id)
        result = await self.session.execute(
            query.order_by(ApplicationDocumentSource.source_type, ApplicationDocumentSource.id)
        )
        return list(result.scalars().all())

    async def list_generation_runs(self, user_id: int, document_id: int) -> list[GenerationRun]:
        result = await self.session.execute(
            select(GenerationRun)
            .where(GenerationRun.document_id == document_id, GenerationRun.user_id == user_id)
            .order_by(GenerationRun.created_at.desc(), GenerationRun.id.desc())
        )
        return list(result.scalars().all())

    async def get_generation_run(
        self, user_id: int, document_id: int, run_id: int
    ) -> GenerationRun | None:
        result = await self.session.execute(
            select(GenerationRun).where(
                GenerationRun.id == run_id,
                GenerationRun.document_id == document_id,
                GenerationRun.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    def _apply_filters(
        self,
        query: Select[tuple[ApplicationDocument]],
        *,
        document_type: ApplicationDocumentType | None,
        status: ApplicationDocumentStatus | None,
        job_id: int | None,
        resume_id: int | None,
        keyword: str | None,
    ) -> Select[tuple[ApplicationDocument]]:
        if document_type:
            query = query.where(ApplicationDocument.document_type == document_type)
        if status:
            query = query.where(ApplicationDocument.status == status)
        if job_id:
            query = query.where(ApplicationDocument.job_id == job_id)
        if resume_id:
            query = query.where(ApplicationDocument.resume_id == resume_id)
        if keyword:
            pattern = f"%{keyword.lower()}%"
            query = query.where(
                or_(
                    func.lower(ApplicationDocument.title).like(pattern),
                    func.lower(ApplicationDocument.question).like(pattern),
                    func.lower(ApplicationDocument.instructions).like(pattern),
                )
            )
        return query
