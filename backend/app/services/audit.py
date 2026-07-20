from __future__ import annotations

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_token
from app.models.audit import AuditLog


def client_ip_hash(request: Request) -> str | None:
    if not request.client:
        return None
    return hash_token(request.client.host)


class AuditLogService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record(
        self,
        *,
        user_id: int | None,
        action: str,
        result: str = "SUCCESS",
        request: Request | None = None,
        resource_type: str | None = None,
        resource_id: str | int | None = None,
        metadata: dict | None = None,
    ) -> AuditLog:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None,
            result=result,
            request_id=getattr(request.state, "request_id", None) if request else None,
            ip_hash=client_ip_hash(request) if request else None,
            user_agent=request.headers.get("user-agent")[:512] if request else None,
            audit_metadata=metadata,
        )
        self.session.add(audit)
        await self.session.commit()
        await self.session.refresh(audit)
        return audit
