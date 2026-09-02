import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EvidenceContext(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    event_type: str = Field(max_length=64)
    outcome: str | None = Field(default=None, max_length=32)
    source_ip: str | None = Field(default=None, max_length=45)
    user_identifier: str | None = Field(default=None, max_length=254)
    endpoint: str | None = Field(default=None, max_length=500)


class AnalysisContext(BaseModel):
    alert_id: uuid.UUID
    title: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    severity: str = Field(max_length=20)
    rule_id: str = Field(max_length=100)
    rule_version: str = Field(max_length=20)
    risk_score: float = Field(ge=0, le=100)
    evidence: list[EvidenceContext] = Field(max_length=100)


class AnalysisResult(BaseModel):
    summary: str = Field(min_length=1, max_length=1500)
    likely_attack: str = Field(min_length=1, max_length=200)
    confidence: float = Field(ge=0, le=1)
    evidence_references: list[uuid.UUID] = Field(min_length=1, max_length=100)
    recommended_actions: list[str] = Field(min_length=1, max_length=8)

    @field_validator("recommended_actions")
    @classmethod
    def bound_actions(cls, values: list[str]) -> list[str]:
        if any(not value.strip() or len(value) > 300 for value in values):
            raise ValueError("recommended actions must contain 1 to 300 characters")
        return values


class AnalysisResponse(AnalysisResult):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    alert_id: uuid.UUID
    provider: str
    model: str
    created_at: datetime
