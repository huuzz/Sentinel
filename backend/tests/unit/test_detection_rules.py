import uuid
from datetime import UTC, datetime, timedelta

from app.detection.risk import calculate_risk
from app.detection.rules import APIVolumeRule, PasswordSprayRule, SuspiciousSuccessRule
from app.models.alert import AlertSeverity
from app.models.security_event import SecurityEvent

START = datetime(2026, 9, 2, 12, tzinfo=UTC)


def event(index: int, **values: object) -> SecurityEvent:
    defaults: dict[str, object] = {
        "id": uuid.uuid4(),
        "timestamp": START + timedelta(seconds=index),
        "event_type": "authentication",
        "source": "test",
        "outcome": "failure",
        "source_ip": "203.0.113.50",
        "user_identifier": "user@example.test",
        "event_metadata": {},
        "simulated": True,
    }
    defaults.update(values)
    return SecurityEvent(**defaults)


def test_password_spray_requires_distinct_identities() -> None:
    same_user = [event(index) for index in range(5)]
    assert PasswordSprayRule(5, 300).evaluate(same_user[-1], same_user) is None
    sprayed = [event(index, user_identifier=f"user-{index}@example.test") for index in range(5)]
    finding = PasswordSprayRule(5, 300).evaluate(sprayed[-1], sprayed)
    assert finding is not None
    assert finding.rule_id == "password_spray"
    assert len(finding.events) == 5


def test_api_volume_counts_only_api_events_from_source() -> None:
    events = [event(index, event_type="api_request", outcome="success") for index in range(30)]
    finding = APIVolumeRule(30, 60).evaluate(events[-1], events)
    assert finding is not None
    assert finding.severity is AlertSeverity.MEDIUM
    assert APIVolumeRule(31, 60).evaluate(events[-1], events) is None


def test_success_after_failures_includes_success_as_evidence() -> None:
    events = [event(index) for index in range(5)]
    success = event(6, outcome="success")
    events.append(success)
    finding = SuspiciousSuccessRule(5, 600).evaluate(success, events)
    assert finding is not None
    assert finding.severity is AlertSeverity.CRITICAL
    assert finding.events[-1] is success


def test_risk_score_is_bounded_and_monotonic() -> None:
    low = calculate_risk(AlertSeverity.MEDIUM, 0.5, 2)
    high = calculate_risk(AlertSeverity.HIGH, 0.9, 10)
    assert 0 <= low < high <= 100
    assert calculate_risk(AlertSeverity.CRITICAL, 2, 1000) == 100
