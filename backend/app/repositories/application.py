from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import (
    Application,
    ApplicationChannel,
    ApplicationNote,
    ApplicationPriority,
    ApplicationStatus,
    ApplicationStatusHistory,
)


class ApplicationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_applications(
        self,
        user_id: int,
        *,
        page: int,
        size: int,
        keyword: str | None = None,
        status: ApplicationStatus | None = None,
        company: str | None = None,
        job_id: int | None = None,
        priority: ApplicationPriority | None = None,
        application_channel: ApplicationChannel | None = None,
        applied_from=None,
        applied_to=None,
        updated_from=None,
        updated_to=None,
        has_document: bool | None = None,
        has_resume: bool | None = None,
        archived: bool = False,
        sort: str = "updated_at",
        order: str = "desc",
    ) -> tuple[list[Application], int]:
        query = select(Application).where(Application.user_id == user_id)
        query = self._apply_filters(
            query,
            keyword=keyword,
            status=status,
            company=company,
            job_id=job_id,
            priority=priority,
            application_channel=application_channel,
            applied_from=applied_from,
            applied_to=applied_to,
            updated_from=updated_from,
            updated_to=updated_to,
            has_document=has_document,
            has_resume=has_resume,
            archived=archived,
        )
        total_result = await self.session.execute(
            select(func.count()).select_from(query.order_by(None).subquery())
        )
        total = int(total_result.scalar_one())
        order_column = self._sort_column(sort)
        if order.lower() == "asc":
            ordering = (order_column.asc(), Application.id.asc())
        else:
            ordering = (order_column.desc(), Application.id.desc())
        result = await self.session.execute(
            query.options(selectinload(Application.notes))
            .order_by(*ordering)
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().unique().all()), total

    async def get_application(
        self, user_id: int, application_id: int, *, include_archived: bool = False
    ) -> Application | None:
        query = (
            select(Application)
            .options(
                selectinload(Application.notes),
                selectinload(Application.status_history),
            )
            .where(Application.id == application_id, Application.user_id == user_id)
            .execution_options(populate_existing=True)
        )
        if not include_archived:
            query = query.where(Application.is_archived.is_(False))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_status_history(
        self, user_id: int, application_id: int
    ) -> list[ApplicationStatusHistory]:
        result = await self.session.execute(
            select(ApplicationStatusHistory)
            .where(
                ApplicationStatusHistory.user_id == user_id,
                ApplicationStatusHistory.application_id == application_id,
            )
            .order_by(ApplicationStatusHistory.changed_at.desc(), ApplicationStatusHistory.id.desc())
        )
        return list(result.scalars().all())

    async def list_notes(self, user_id: int, application_id: int) -> list[ApplicationNote]:
        result = await self.session.execute(
            select(ApplicationNote)
            .where(ApplicationNote.user_id == user_id, ApplicationNote.application_id == application_id)
            .order_by(ApplicationNote.is_pinned.desc(), ApplicationNote.updated_at.desc(), ApplicationNote.id.desc())
        )
        return list(result.scalars().all())

    async def get_note(self, user_id: int, application_id: int, note_id: int) -> ApplicationNote | None:
        result = await self.session.execute(
            select(ApplicationNote).where(
                ApplicationNote.id == note_id,
                ApplicationNote.user_id == user_id,
                ApplicationNote.application_id == application_id,
            )
        )
        return result.scalar_one_or_none()

    def _apply_filters(
        self,
        query: Select[tuple[Application]],
        *,
        keyword: str | None,
        status: ApplicationStatus | None,
        company: str | None,
        job_id: int | None,
        priority: ApplicationPriority | None,
        application_channel: ApplicationChannel | None,
        applied_from,
        applied_to,
        updated_from,
        updated_to,
        has_document: bool | None,
        has_resume: bool | None,
        archived: bool,
    ) -> Select[tuple[Application]]:
        query = query.where(Application.is_archived.is_(archived))
        if keyword:
            pattern = f"%{keyword.lower()}%"
            query = query.where(
                or_(
                    func.lower(Application.company_name_snapshot).like(pattern),
                    func.lower(Application.job_title_snapshot).like(pattern),
                    func.lower(Application.contact_name).like(pattern),
                    func.lower(Application.source).like(pattern),
                )
            )
        if status:
            query = query.where(Application.status == status)
        if company:
            query = query.where(func.lower(Application.company_name_snapshot).like(f"%{company.lower()}%"))
        if job_id:
            query = query.where(Application.job_id == job_id)
        if priority:
            query = query.where(Application.priority == priority)
        if application_channel:
            query = query.where(Application.application_channel == application_channel)
        if applied_from:
            query = query.where(Application.applied_at >= applied_from)
        if applied_to:
            query = query.where(Application.applied_at <= applied_to)
        if updated_from:
            query = query.where(Application.updated_at >= updated_from)
        if updated_to:
            query = query.where(Application.updated_at <= updated_to)
        if has_document is not None:
            query = query.where(Application.application_document_id.is_not(None) if has_document else Application.application_document_id.is_(None))
        if has_resume is not None:
            query = query.where(Application.resume_id.is_not(None) if has_resume else Application.resume_id.is_(None))
        return query

    def _sort_column(self, sort: str):
        return {
            "created_at": Application.created_at,
            "updated_at": Application.updated_at,
            "applied_at": Application.applied_at,
            "planned_apply_at": Application.planned_apply_at,
            "company_name": Application.company_name_snapshot,
            "status": Application.status,
            "priority": Application.priority,
        }.get(sort, Application.updated_at)
