import uuid
from datetime import UTC, datetime, timedelta

from app.detection.rules import BruteForceRule
from app.models.security_event import SecurityEvent


def failed_event(index: int, source_ip: str = "198.51.100.42") -> SecurityEvent:
    return SecurityEvent(
        id=uuid.uuid4(),
        timestamp=datetime(2026, 8, 31, 12, 0, tzinfo=UTC) + timedelta(seconds=index * 5),
        event_type="authentication",
        source="test",
        outcome="failure",
        source_ip=source_ip,
        event_metadata={},
        simulated=True,
    )


def test_brute_force_requires_threshold() -> None:
    events = [failed_event(index) for index in range(9)]
    assert BruteForceRule(10, 120).evaluate(events[-1], events) is None


def test_brute_force_returns_explainable_finding() -> None:
    events = [failed_event(index) for index in range(10)]
    finding = BruteForceRule(10, 120).evaluate(events[-1], events)
    assert finding is not None
    assert finding.rule_id == "brute_force"
    assert finding.risk_score == 88.0
    assert len(finding.events) == 10
    assert "198.51.100.42" in finding.deduplication_key


def test_success_does_not_trigger() -> None:
    events = [failed_event(index) for index in range(10)]
    events[-1].outcome = "success"
    assert BruteForceRule(10, 120).evaluate(events[-1], events) is None
