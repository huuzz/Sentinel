from datetime import timedelta

from app.detection.base import DetectionFinding
from app.models.alert import AlertSeverity
from app.models.security_event import SecurityEvent


class BruteForceRule:
    rule_id = "brute_force"
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
        ]
        if len(matching) < self.threshold:
            return None
        bucket = int(current.timestamp.timestamp()) // self.window_seconds
        return DetectionFinding(
            rule_id=self.rule_id,
            rule_version=self.rule_version,
            title="Possible brute-force authentication attack",
            description=(
                f"Detected {len(matching)} failed authentication attempts from "
                f"{current.source_ip} within {timedelta(seconds=self.window_seconds)}."
            ),
            severity=AlertSeverity.HIGH,
            risk_score=80.0,
            deduplication_key=f"{self.rule_id}:{current.source_ip}:{bucket}",
            events=matching,
        )
