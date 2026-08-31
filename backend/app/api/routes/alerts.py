import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.events import event_response
from app.db.session import get_session
from app.models.alert import AlertSeverity, AlertStatus
from app.models.security_event import SecurityEvent
from app.repositories.alerts import AlertRepository
from app.schemas.alerts import AlertDetailResponse, AlertListResponse, AlertResponse

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])
DatabaseSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    session: DatabaseSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    severity: AlertSeverity | None = None,
    status: AlertStatus | None = None,
    rule: Annotated[str | None, Query(max_length=100)] = None,
) -> AlertListResponse:
    alerts = await AlertRepository(session).list(
        limit=limit, severity=severity, status=status, rule=rule
    )
    return AlertListResponse(items=[AlertResponse.model_validate(alert) for alert in alerts])


@router.get("/{alert_id}", response_model=AlertDetailResponse)
async def get_alert(alert_id: uuid.UUID, session: DatabaseSession) -> AlertDetailResponse:
    alert = await AlertRepository(session).get(alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    event_ids = [link.event_id for link in alert.evidence]
    events = list(
        await session.scalars(
            select(SecurityEvent)
            .where(SecurityEvent.id.in_(event_ids))
            .order_by(SecurityEvent.timestamp)
        )
    )
    event_responses = [event_response(event) for event in events]
    values = AlertResponse.model_validate(alert).model_dump()
    return AlertDetailResponse(**values, supporting_events=event_responses)
