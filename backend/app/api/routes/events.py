import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import AnalystUser, ViewerUser
from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.models.security_event import SecurityEvent
from app.repositories.events import EventRepository
from app.schemas.events import (
    EventIngestResponse,
    EventListResponse,
    SecurityEventCreate,
    SecurityEventResponse,
)
from app.services.ingestion import IngestionService

router = APIRouter(prefix="/api/v1/events", tags=["events"])
DatabaseSession = Annotated[AsyncSession, Depends(get_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def event_response(event: SecurityEvent) -> SecurityEventResponse:
    return SecurityEventResponse.model_validate(
        {
            "id": event.id,
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "source": event.source,
            "outcome": event.outcome,
            "user_identifier": event.user_identifier,
            "source_ip": event.source_ip,
            "endpoint": event.endpoint,
            "http_method": event.http_method,
            "status_code": event.status_code,
            "metadata": event.event_metadata,
            "simulated": event.simulated,
            "created_at": event.created_at,
        }
    )


@router.post("", response_model=EventIngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_event(
    payload: SecurityEventCreate, session: DatabaseSession, settings: AppSettings, _: AnalystUser
) -> EventIngestResponse:
    event, alert_ids = await IngestionService(session, settings).ingest(payload)
    return EventIngestResponse(
        event=event_response(event), alert_ids=[uuid.UUID(value) for value in alert_ids]
    )


@router.get("", response_model=EventListResponse)
async def list_events(
    session: DatabaseSession,
    _: ViewerUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    event_type: Annotated[str | None, Query(max_length=64)] = None,
    source_ip: Annotated[str | None, Query(max_length=45)] = None,
    user_identifier: Annotated[str | None, Query(max_length=254)] = None,
    source: Annotated[str | None, Query(max_length=100)] = None,
) -> EventListResponse:
    events = await EventRepository(session).list(
        limit=limit,
        event_type=event_type,
        source_ip=source_ip,
        user_identifier=user_identifier,
        source=source,
    )
    return EventListResponse(items=[event_response(event) for event in events])


@router.get("/{event_id}", response_model=SecurityEventResponse)
async def get_event(
    event_id: uuid.UUID, session: DatabaseSession, _: ViewerUser
) -> SecurityEventResponse:
    event = await EventRepository(session).get(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Security event not found")
    return event_response(event)
