from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.resume import Resume, ResumeFile, ResumeFileExtraction


class ResumeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_resumes(self, user_id: int, page: int, size: int) -> tuple[list[Resume], int]:
        base = select(Resume).where(Resume.user_id == user_id)
        total_result = await self.session.execute(
            select(func.count()).select_from(base.order_by(None).subquery())
        )
        total = int(total_result.scalar_one())
        result = await self.session.execute(
            base.options(selectinload(Resume.files))
            .order_by(Resume.is_default.desc(), Resume.updated_at.desc(), Resume.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().all()), total

    async def get_resume(self, user_id: int, resume_id: int) -> Resume | None:
        result = await self.session.execute(
            select(Resume)
            .options(selectinload(Resume.files))
            .where(Resume.id == resume_id, Resume.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_file(self, user_id: int, resume_id: int, file_id: int) -> ResumeFile | None:
        result = await self.session.execute(
            select(ResumeFile).where(
                ResumeFile.id == file_id,
                ResumeFile.resume_id == resume_id,
                ResumeFile.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_duplicate_file_hash(self, user_id: int, file_hash: str) -> ResumeFile | None:
        result = await self.session.execute(
            select(ResumeFile).where(ResumeFile.user_id == user_id, ResumeFile.file_hash == file_hash)
        )
        return result.scalar_one_or_none()

    async def get_extraction(self, user_id: int, resume_file_id: int) -> ResumeFileExtraction | None:
        result = await self.session.execute(
            select(ResumeFileExtraction).where(
                ResumeFileExtraction.user_id == user_id,
                ResumeFileExtraction.resume_file_id == resume_file_id,
            )
        )
        return result.scalar_one_or_none()

    async def clear_default(self, user_id: int) -> None:
        await self.session.execute(update(Resume).where(Resume.user_id == user_id).values(is_default=False))
