from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application_document import ApplicationDocument, ApplicationDocumentVersion
from app.models.document_improvement import DocumentImprovementRun, DocumentImprovementSuggestion


class DocumentImprovementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_document(self, user_id: int, document_id: int) -> ApplicationDocument | None:
        result = await self.session.execute(
            select(ApplicationDocument)
            .options(selectinload(ApplicationDocument.versions))
            .where(
                ApplicationDocument.id == document_id,
                ApplicationDocument.user_id == user_id,
                ApplicationDocument.is_archived.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_version(self, user_id: int, document_id: int, version_id: int) -> ApplicationDocumentVersion | None:
        return await self.session.scalar(
            select(ApplicationDocumentVersion).where(
                ApplicationDocumentVersion.id == version_id,
                ApplicationDocumentVersion.user_id == user_id,
                ApplicationDocumentVersion.document_id == document_id,
            )
        )

    async def latest_version(self, user_id: int, document_id: int) -> ApplicationDocumentVersion | None:
        result = await self.session.execute(
            select(ApplicationDocumentVersion)
            .where(
                ApplicationDocumentVersion.user_id == user_id,
                ApplicationDocumentVersion.document_id == document_id,
            )
            .order_by(ApplicationDocumentVersion.version_number.desc(), ApplicationDocumentVersion.id.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def latest_version_number(self, document_id: int) -> int:
        result = await self.session.execute(
            select(func.coalesce(func.max(ApplicationDocumentVersion.version_number), 0)).where(
                ApplicationDocumentVersion.document_id == document_id
            )
        )
        return int(result.scalar_one())

    async def list_runs(self, user_id: int, document_id: int, page: int, size: int) -> tuple[list[DocumentImprovementRun], int]:
        base = select(DocumentImprovementRun).where(
            DocumentImprovementRun.user_id == user_id,
            DocumentImprovementRun.application_document_id == document_id,
        )
        total_result = await self.session.execute(select(func.count()).select_from(base.order_by(None).subquery()))
        total = int(total_result.scalar_one())
        result = await self.session.execute(
            base.options(
                selectinload(DocumentImprovementRun.suggestions),
                selectinload(DocumentImprovementRun.sources),
                selectinload(DocumentImprovementRun.actions),
            )
            .order_by(DocumentImprovementRun.created_at.desc(), DocumentImprovementRun.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().unique().all()), total

    async def get_run(self, user_id: int, document_id: int, run_id: int) -> DocumentImprovementRun | None:
        result = await self.session.execute(
            select(DocumentImprovementRun)
            .options(
                selectinload(DocumentImprovementRun.suggestions),
                selectinload(DocumentImprovementRun.sources),
                selectinload(DocumentImprovementRun.actions),
            )
            .where(
                DocumentImprovementRun.id == run_id,
                DocumentImprovementRun.user_id == user_id,
                DocumentImprovementRun.application_document_id == document_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_suggestion(self, run_id: int, suggestion_id: int) -> DocumentImprovementSuggestion | None:
        return await self.session.scalar(
            select(DocumentImprovementSuggestion).where(
                DocumentImprovementSuggestion.id == suggestion_id,
                DocumentImprovementSuggestion.run_id == run_id,
            )
        )
