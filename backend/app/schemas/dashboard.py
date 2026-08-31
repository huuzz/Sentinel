from datetime import datetime

from pydantic import BaseModel

from app.schemas.alerts import AlertResponse


class NamedCount(BaseModel):
    name: str
    count: int


class TimeCount(BaseModel):
    timestamp: datetime
    count: int


class DashboardSummary(BaseModel):
    total_events: int
    alerts_today: int
    alerts_by_severity: list[NamedCount]
    common_event_types: list[NamedCount]
    event_volume: list[TimeCount]
    recent_alerts: list[AlertResponse]
