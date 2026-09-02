from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import AdminUser
from app.db.session import get_session
from app.models.user import AuditLog
from app.schemas.audit import AuditLogResponse

router = APIRouter(prefix="/api/v1/audit-logs", tags=["audit"])


@router.get("", response_model=list[AuditLogResponse])
async def list_audit_logs(
    session: Annotated[AsyncSession, Depends(get_session)],
    _: AdminUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[AuditLog]:
    return list(
        await session.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit))
    )
