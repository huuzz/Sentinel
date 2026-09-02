import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import AIAnalyzer
from app.ai.provider import get_analyzer
from app.api.dependencies import AnalystUser, ViewerUser
from app.db.session import get_session
from app.models.ai_analysis import AIAnalysis
from app.models.user import AuditLog
from app.schemas.analysis import AnalysisResponse
from app.services.analysis import AnalysisService

router = APIRouter(prefix="/api/v1/alerts/{alert_id}/analysis", tags=["analysis"])
DatabaseSession = Annotated[AsyncSession, Depends(get_session)]
Analyzer = Annotated[AIAnalyzer, Depends(get_analyzer)]


def response_for(analysis: AIAnalysis) -> AnalysisResponse:
    return AnalysisResponse.model_validate(
        {
            "id": analysis.id,
            "alert_id": analysis.alert_id,
            "summary": analysis.summary,
            "likely_attack": analysis.likely_attack,
            "confidence": analysis.confidence,
            "evidence_references": analysis.evidence_references,
            "recommended_actions": analysis.recommended_actions,
            "provider": analysis.provider,
            "model": analysis.model,
            "created_at": analysis.created_at,
        }
    )


@router.post("", response_model=AnalysisResponse)
async def analyze_alert(
    alert_id: uuid.UUID, session: DatabaseSession, user: AnalystUser, analyzer: Analyzer
) -> AnalysisResponse:
    analysis = await AnalysisService(session, analyzer).analyze(alert_id)
    session.add(
        AuditLog(
            actor_user_id=user.id,
            action="alert.analyze",
            target_type="alert",
            target_id=str(alert_id),
            outcome="SUCCESS",
            details={"provider": analysis.provider, "model": analysis.model},
        )
    )
    await session.commit()
    return response_for(analysis)


@router.get("", response_model=AnalysisResponse)
async def get_analysis(
    alert_id: uuid.UUID, session: DatabaseSession, _: ViewerUser
) -> AnalysisResponse:
    analysis = await AnalysisService(session, get_analyzer()).get(alert_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return response_for(analysis)
