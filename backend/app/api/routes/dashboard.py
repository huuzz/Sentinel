from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.alert import Alert
from app.models.security_event import SecurityEvent
from app.schemas.alerts import AlertResponse
from app.schemas.dashboard import DashboardSummary, NamedCount, TimeCount

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])
DatabaseSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(session: DatabaseSession) -> DashboardSummary:
    now = datetime.now(UTC)
    start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_volume = now - timedelta(hours=24)
    total_events = await session.scalar(select(func.count()).select_from(SecurityEvent)) or 0
    alerts_today = (
        await session.scalar(
            select(func.count()).select_from(Alert).where(Alert.created_at >= start_today)
        )
        or 0
    )
    severity_rows = await session.execute(
        select(Alert.severity, func.count(Alert.id)).group_by(Alert.severity)
    )
    type_rows = await session.execute(
        select(SecurityEvent.event_type, func.count(SecurityEvent.id))
        .group_by(SecurityEvent.event_type)
        .order_by(desc(func.count(SecurityEvent.id)))
        .limit(5)
    )
    bucket = func.date_trunc("hour", SecurityEvent.timestamp)
    volume_rows = await session.execute(
        select(bucket, func.count(SecurityEvent.id))
        .where(SecurityEvent.timestamp >= start_volume)
        .group_by(bucket)
        .order_by(bucket)
    )
    recent = list(await session.scalars(select(Alert).order_by(Alert.created_at.desc()).limit(5)))
    return DashboardSummary(
        total_events=total_events,
        alerts_today=alerts_today,
        alerts_by_severity=[NamedCount(name=row[0].value, count=row[1]) for row in severity_rows],
        common_event_types=[NamedCount(name=row[0], count=row[1]) for row in type_rows],
        event_volume=[TimeCount(timestamp=row[0], count=row[1]) for row in volume_rows],
        recent_alerts=[AlertResponse.model_validate(alert) for alert in recent],
    )
