from datetime import timedelta

from app.detection.base import DetectionFinding
from app.detection.risk import calculate_risk
from app.models.alert import AlertSeverity
from app.models.security_event import SecurityEvent


class APIVolumeRule:
    rule_id = "api_volume_abuse"
    rule_version = "1.0"

    def __init__(self, threshold: int, window_seconds: int) -> None:
        self.threshold = threshold
        self.window_seconds = window_seconds

    def evaluate(
        self, current: SecurityEvent, events: list[SecurityEvent]
    ) -> DetectionFinding | None:
        if current.event_type != "api_request" or not current.source_ip:
            return None
        matching = [
            event
            for event in events
            if event.event_type == "api_request" and event.source_ip == current.source_ip
        ]
        if len(matching) < self.threshold:
            return None
        severity = AlertSeverity.MEDIUM
        return DetectionFinding(
            rule_id=self.rule_id,
            rule_version=self.rule_version,
            title="Unusually high API request volume",
            description=(
                f"Detected {len(matching)} API requests from {current.source_ip} "
                f"within {timedelta(seconds=self.window_seconds)}."
            ),
            severity=severity,
            risk_score=calculate_risk(severity, 0.7, len(matching)),
            deduplication_key=f"{self.rule_id}:{current.source_ip}",
            events=matching,
        )
