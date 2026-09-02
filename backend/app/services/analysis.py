import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import AIAnalyzer
from app.models.ai_analysis import AIAnalysis
from app.models.security_event import SecurityEvent
from app.repositories.alerts import AlertRepository
from app.schemas.analysis import AnalysisContext, AnalysisResult, EvidenceContext


class AnalysisService:
    def __init__(self, session: AsyncSession, analyzer: AIAnalyzer) -> None:
        self.session = session
        self.analyzer = analyzer

    async def analyze(self, alert_id: uuid.UUID) -> AIAnalysis:
        alert = await AlertRepository(self.session).get(alert_id)
        if alert is None:
            raise HTTPException(status_code=404, detail="Alert not found")
        event_ids = [link.event_id for link in alert.evidence][:100]
        events = list(
            await self.session.scalars(
                select(SecurityEvent)
                .where(SecurityEvent.id.in_(event_ids))
                .order_by(SecurityEvent.timestamp)
            )
        )
        if not events:
            raise HTTPException(status_code=422, detail="Alert has no evidence to analyze")
        context = AnalysisContext(
            alert_id=alert.id,
            title=alert.title,
            description=alert.description[:1000],
            severity=alert.severity.value,
            rule_id=alert.detection_rule,
            rule_version=alert.rule_version,
            risk_score=alert.risk_score,
            evidence=[
                EvidenceContext(
                    id=event.id,
                    timestamp=event.timestamp,
                    event_type=event.event_type,
                    outcome=event.outcome,
                    source_ip=event.source_ip,
                    user_identifier=event.user_identifier,
                    endpoint=event.endpoint,
                )
                for event in events
            ],
        )
        result = AnalysisResult.model_validate(await self.analyzer.analyze(context))
        allowed_ids = {event.id for event in events}
        if not set(result.evidence_references).issubset(allowed_ids):
            raise HTTPException(
                status_code=502, detail="Analyzer returned invalid evidence references"
            )
        existing = await self.get(alert_id)
        values = {
            "summary": result.summary,
            "likely_attack": result.likely_attack,
            "confidence": result.confidence,
            "evidence_references": [str(value) for value in result.evidence_references],
            "recommended_actions": result.recommended_actions,
            "provider": self.analyzer.provider,
            "model": self.analyzer.model,
        }
        if existing is None:
            existing = AIAnalysis(alert_id=alert.id, **values)
            self.session.add(existing)
        else:
            for field, value in values.items():
                setattr(existing, field, value)
        await self.session.flush()
        return existing

    async def get(self, alert_id: uuid.UUID) -> AIAnalysis | None:
        result: AIAnalysis | None = await self.session.scalar(
            select(AIAnalysis).where(AIAnalysis.alert_id == alert_id)
        )
        return result
