import uuid
from datetime import datetime

from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.security_event import SecurityEvent
from app.schemas.events import SecurityEventCreate


class EventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: SecurityEventCreate) -> SecurityEvent:
        values = payload.model_dump(exclude={"metadata"})
        event = SecurityEvent(**values, event_metadata=payload.metadata)
        self.session.add(event)
        await self.session.flush()
        return event

    async def get(self, event_id: uuid.UUID) -> SecurityEvent | None:
        return await self.session.get(SecurityEvent, event_id)

    async def recent_failures(
        self, source_ip: str, start: datetime, end: datetime
    ) -> list[SecurityEvent]:
        result = await self.session.scalars(
            select(SecurityEvent)
            .where(
                SecurityEvent.event_type == "authentication",
                SecurityEvent.outcome == "failure",
                SecurityEvent.source_ip == source_ip,
                SecurityEvent.timestamp >= start,
                SecurityEvent.timestamp <= end,
            )
            .order_by(SecurityEvent.timestamp, SecurityEvent.id)
            .limit(1000)
        )
        return list(result)

    async def list(
        self,
        *,
        limit: int,
        event_type: str | None,
        source_ip: str | None,
        user_identifier: str | None,
        source: str | None,
    ) -> list[SecurityEvent]:
        query: Select[tuple[SecurityEvent]] = select(SecurityEvent)
        filters = []
        if event_type:
            filters.append(SecurityEvent.event_type == event_type)
        if source_ip:
            filters.append(SecurityEvent.source_ip == source_ip)
        if user_identifier:
            filters.append(SecurityEvent.user_identifier == user_identifier)
        if source:
            filters.append(SecurityEvent.source == source)
        if filters:
            query = query.where(and_(*filters))
        result = await self.session.scalars(
            query.order_by(SecurityEvent.timestamp.desc(), SecurityEvent.id.desc()).limit(limit)
        )
        return list(result)
