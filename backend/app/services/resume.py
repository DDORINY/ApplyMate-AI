import hashlib
from math import ceil

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.security import utc_now
from app.models.resume import Resume, ResumeFile
from app.repositories.resume import ResumeRepository
from app.schemas.resume import ResumeCreate, ResumeListData, ResumePublic, ResumeUpdate
from app.services.storage import LocalFileStorage


class ResumeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ResumeRepository(session)
        self.storage = LocalFileStorage()

    async def create_resume(self, user_id: int, payload: ResumeCreate) -> Resume:
        if payload.is_default:
            await self.repository.clear_default(user_id)
        resume = Resume(user_id=user_id, **payload.model_dump())
        self.session.add(resume)
        await self.session.commit()
        return await self.get_resume(user_id, resume.id)

    async def list_resumes(self, user_id: int, page: int, size: int) -> ResumeListData:
        resumes, total = await self.repository.list_resumes(user_id, page, size)
        return ResumeListData(
            items=[ResumePublic.model_validate(resume) for resume in resumes],
            page=page,
            size=size,
            total=total,
            total_pages=ceil(total / size) if total else 0,
        )

    async def get_resume(self, user_id: int, resume_id: int) -> Resume:
        resume = await self.repository.get_resume(user_id, resume_id)
        if not resume:
            raise AppError("RESUME_NOT_FOUND", "이력서를 찾을 수 없습니다.", 404)
        return resume

    async def update_resume(self, user_id: int, resume_id: int, payload: ResumeUpdate) -> Resume:
        resume = await self.get_resume(user_id, resume_id)
        data = payload.model_dump(exclude_unset=True)
        if data.get("is_default") is True:
            await self.repository.clear_default(user_id)
        for key, value in data.items():
            setattr(resume, key, value)
        await self.session.commit()
        return await self.get_resume(user_id, resume_id)

    async def set_default(self, user_id: int, resume_id: int) -> Resume:
        resume = await self.get_resume(user_id, resume_id)
        await self.repository.clear_default(user_id)
        resume.is_default = True
        await self.session.commit()
        return await self.get_resume(user_id, resume_id)

    async def delete_resume(self, user_id: int, resume_id: int) -> None:
        resume = await self.get_resume(user_id, resume_id)
        paths = [file.storage_path for file in resume.files]
        await self.session.delete(resume)
        await self.session.commit()
        for path in paths:
            self.storage.delete(path)

    async def upload_file(self, user_id: int, resume_id: int, upload: UploadFile) -> ResumeFile:
        await self.get_resume(user_id, resume_id)
        stored = await self.storage.validate_and_read(upload)
        file_hash = hashlib.sha256(stored.content).hexdigest()
        duplicate = await self.repository.get_duplicate_file_hash(user_id, file_hash)
        if duplicate:
            raise AppError("RESUME_FILE_ALREADY_EXISTS", "이미 업로드한 이력서 파일입니다.", 409)

        self.storage.save(stored)
        resume_file = ResumeFile(
            resume_id=resume_id,
            user_id=user_id,
            original_filename=stored.original_filename,
            stored_filename=stored.stored_filename,
            storage_path=stored.storage_path,
            content_type=stored.content_type,
            file_extension=stored.file_extension,
            file_size=stored.file_size,
            file_hash=file_hash,
            uploaded_at=utc_now(),
        )
        self.session.add(resume_file)
        try:
            await self.session.commit()
        except Exception:
            self.storage.delete(stored.storage_path)
            raise
        await self.session.refresh(resume_file)
        return resume_file

    async def get_file(self, user_id: int, resume_id: int, file_id: int) -> ResumeFile:
        resume_file = await self.repository.get_file(user_id, resume_id, file_id)
        if not resume_file:
            raise AppError("RESUME_FILE_NOT_FOUND", "이력서 파일을 찾을 수 없습니다.", 404)
        return resume_file

    async def delete_file(self, user_id: int, resume_id: int, file_id: int) -> None:
        resume_file = await self.get_file(user_id, resume_id, file_id)
        storage_path = resume_file.storage_path
        await self.session.delete(resume_file)
        await self.session.commit()
        self.storage.delete(storage_path)
