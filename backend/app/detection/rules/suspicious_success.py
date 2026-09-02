from datetime import timedelta

from app.detection.base import DetectionFinding
from app.detection.risk import calculate_risk
from app.models.alert import AlertSeverity
from app.models.security_event import SecurityEvent


class SuspiciousSuccessRule:
    rule_id = "failed_login_then_success"
    rule_version = "1.0"

    def __init__(self, failure_threshold: int, window_seconds: int) -> None:
        self.failure_threshold = failure_threshold
        self.window_seconds = window_seconds

    def evaluate(
        self, current: SecurityEvent, events: list[SecurityEvent]
    ) -> DetectionFinding | None:
        if (
            current.event_type != "authentication"
            or current.outcome != "success"
            or not current.user_identifier
            or not current.source_ip
        ):
            return None
        failures = [
            event
            for event in events
            if event.event_type == "authentication"
            and event.outcome == "failure"
            and event.user_identifier == current.user_identifier
            and event.source_ip == current.source_ip
            and event.timestamp <= current.timestamp
        ]
        if len(failures) < self.failure_threshold:
            return None
        evidence = [*failures, current]
        severity = AlertSeverity.CRITICAL
        return DetectionFinding(
            rule_id=self.rule_id,
            rule_version=self.rule_version,
            title="Successful login after repeated failures",
            description=(
                f"A successful authentication followed {len(failures)} failures for the same "
                f"identity and source within {timedelta(seconds=self.window_seconds)}."
            ),
            severity=severity,
            risk_score=calculate_risk(severity, 0.9, len(evidence)),
            deduplication_key=f"{self.rule_id}:{current.source_ip}:{current.user_identifier}",
            events=evidence,
        )
