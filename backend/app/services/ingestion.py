from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.detection.rules import BruteForceRule
from app.models.security_event import SecurityEvent
from app.repositories.alerts import AlertRepository
from app.repositories.events import EventRepository
from app.schemas.events import SecurityEventCreate


class IngestionService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.events = EventRepository(session)
        self.alerts = AlertRepository(session)
        self.rule = BruteForceRule(
            threshold=settings.brute_force_threshold,
            window_seconds=settings.brute_force_window_seconds,
        )

    async def ingest(self, payload: SecurityEventCreate) -> tuple[SecurityEvent, list[str]]:
        async with self.session.begin():
            event = await self.events.create(payload)
            alert_ids: list[str] = []
            if event.source_ip:
                recent = await self.events.recent_failures(
                    event.source_ip,
                    event.timestamp - timedelta(seconds=self.rule.window_seconds),
                    event.timestamp,
                )
                finding = self.rule.evaluate(event, recent)
                if finding:
                    alert = await self.alerts.upsert_finding(finding)
                    alert_ids.append(str(alert.id))
        return event, alert_ids
