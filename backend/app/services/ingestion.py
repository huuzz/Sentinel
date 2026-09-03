from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.detection.base import DetectionRule
from app.detection.rules import (
    APIVolumeRule,
    BruteForceRule,
    PasswordSprayRule,
    SuspiciousSuccessRule,
)
from app.ml.runtime import ml_runtime
from app.models.anomaly_score import AnomalyScore
from app.models.security_event import SecurityEvent
from app.repositories.alerts import AlertRepository
from app.repositories.events import EventRepository
from app.schemas.events import SecurityEventCreate


class IngestionService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.events = EventRepository(session)
        self.alerts = AlertRepository(session)
        self.settings = settings
        self.rules: list[DetectionRule] = [
            BruteForceRule(settings.brute_force_threshold, settings.brute_force_window_seconds),
            PasswordSprayRule(
                settings.password_spray_threshold, settings.password_spray_window_seconds
            ),
            APIVolumeRule(settings.api_volume_threshold, settings.api_volume_window_seconds),
            SuspiciousSuccessRule(
                settings.suspicious_success_failure_threshold,
                settings.suspicious_success_window_seconds,
            ),
        ]

    async def ingest(self, payload: SecurityEventCreate) -> tuple[SecurityEvent, list[str]]:
        async with self.session.begin():
            event = await self.events.create(payload)
            inference = ml_runtime.predict(event) if self.settings.ml_enabled else None
            if inference:
                event.anomaly_score = AnomalyScore(
                    score=inference.score,
                    is_anomaly=inference.is_anomaly,
                    model_version=inference.model_version,
                    feature_schema_version=inference.feature_schema_version,
                )
            alert_ids: list[str] = []
            max_window = max(rule.window_seconds for rule in self.rules)
            recent = await self.events.recent_related(
                event, event.timestamp - timedelta(seconds=max_window)
            )
            for rule in self.rules:
                cutoff = event.timestamp - timedelta(seconds=rule.window_seconds)
                scoped = [candidate for candidate in recent if candidate.timestamp >= cutoff]
                finding = rule.evaluate(event, scoped)
                if finding:
                    alert = await self.alerts.upsert_finding(finding)
                    alert_ids.append(str(alert.id))
        return event, alert_ids
