import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.alert import AlertSeverity, AlertStatus
from app.schemas.events import SecurityEventResponse


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    risk_score: float
    detection_rule: str
    rule_version: str
    created_at: datetime
    updated_at: datetime


class AlertDetailResponse(AlertResponse):
    supporting_events: list[SecurityEventResponse]


class AlertListResponse(BaseModel):
    items: list[AlertResponse]
    next_cursor: str | None = None
