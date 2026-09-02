import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.detection.base import DetectionFinding
from app.models.alert import Alert, AlertEvent, AlertSeverity, AlertStatus


class AlertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_finding(self, finding: DetectionFinding) -> Alert:
        alert = await self.session.scalar(
            select(Alert)
            .where(Alert.deduplication_key == finding.deduplication_key)
            .options(selectinload(Alert.evidence))
        )
        if alert is None:
            alert = Alert(
                title=finding.title,
                description=finding.description,
                severity=finding.severity,
                status=AlertStatus.OPEN,
                risk_score=finding.risk_score,
                detection_rule=finding.rule_id,
                rule_version=finding.rule_version,
                deduplication_key=finding.deduplication_key,
                evidence=[AlertEvent(event_id=event.id) for event in finding.events],
            )
            self.session.add(alert)
            await self.session.flush()
        else:
            existing = {link.event_id for link in alert.evidence}
            for event in finding.events:
                if event.id not in existing:
                    alert.evidence.append(AlertEvent(event_id=event.id))
        await self.session.flush()
        return alert

    async def get(self, alert_id: uuid.UUID) -> Alert | None:
        alert: Alert | None = await self.session.scalar(
            select(Alert).where(Alert.id == alert_id).options(selectinload(Alert.evidence))
        )
        return alert

    async def list(
        self,
        *,
        limit: int,
        severity: AlertSeverity | None = None,
        status: AlertStatus | None = None,
        rule: str | None = None,
    ) -> list[Alert]:
        query = select(Alert)
        if severity:
            query = query.where(Alert.severity == severity)
        if status:
            query = query.where(Alert.status == status)
        if rule:
            query = query.where(Alert.detection_rule == rule)
        result = await self.session.scalars(
            query.order_by(Alert.created_at.desc(), Alert.id.desc()).limit(limit)
        )
        return list(result)
