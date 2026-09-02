from datetime import timedelta

from app.detection.base import DetectionFinding
from app.detection.risk import calculate_risk
from app.models.alert import AlertSeverity
from app.models.security_event import SecurityEvent


class PasswordSprayRule:
    rule_id = "password_spray"
    rule_version = "1.0"

    def __init__(self, threshold: int, window_seconds: int) -> None:
        self.threshold = threshold
        self.window_seconds = window_seconds

    def evaluate(
        self, current: SecurityEvent, events: list[SecurityEvent]
    ) -> DetectionFinding | None:
        if (
            current.event_type != "authentication"
            or current.outcome != "failure"
            or not current.source_ip
        ):
            return None
        matching = [
            event
            for event in events
            if event.event_type == "authentication"
            and event.outcome == "failure"
            and event.source_ip == current.source_ip
            and event.user_identifier
        ]
        identities = {event.user_identifier for event in matching}
        if len(identities) < self.threshold:
            return None
        severity = AlertSeverity.HIGH
        return DetectionFinding(
            rule_id=self.rule_id,
            rule_version=self.rule_version,
            title="Possible password-spraying attack",
            description=(
                f"Detected failed authentication attempts against {len(identities)} identities "
                f"from {current.source_ip} within {timedelta(seconds=self.window_seconds)}."
            ),
            severity=severity,
            risk_score=calculate_risk(severity, 0.85, len(matching)),
            deduplication_key=f"{self.rule_id}:{current.source_ip}",
            events=matching,
        )
