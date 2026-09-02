from dataclasses import dataclass
from typing import Protocol

from app.models.alert import AlertSeverity
from app.models.security_event import SecurityEvent


@dataclass(frozen=True)
class DetectionFinding:
    rule_id: str
    rule_version: str
    title: str
    description: str
    severity: AlertSeverity
    risk_score: float
    deduplication_key: str
    events: list[SecurityEvent]


class DetectionRule(Protocol):
    rule_id: str
    rule_version: str
    window_seconds: int

    def evaluate(
        self, current: SecurityEvent, events: list[SecurityEvent]
    ) -> DetectionFinding | None: ...
