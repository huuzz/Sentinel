from datetime import UTC, datetime

import pytest

from app.detection.rules import APIVolumeRule, BruteForceRule
from app.models.security_event import SecurityEvent
from app.services.demo import DEMO_SOURCE, demo_events, require_development


def test_demo_is_deterministic_bounded_and_synthetic() -> None:
    anchor = datetime(2026, 1, 1, tzinfo=UTC)
    events = demo_events(anchor)
    assert events == demo_events(anchor)
    assert len(events) == 45
    assert all(event.simulated and event.source == DEMO_SOURCE for event in events)
    assert {event.source_ip for event in events} == {"198.51.100.201", "203.0.113.201"}
    assert sum(event.outcome == "failure" for event in events) == 10
    assert sum(event.event_type == "api_request" for event in events) == 30
    assert len({event.metadata["seed_index"] for event in events}) == 45


@pytest.mark.parametrize("environment", ["production", "staging", "test", "Development"])
def test_demo_refuses_non_development(environment: str) -> None:
    with pytest.raises(ValueError, match="only in development"):
        require_development(environment)


def test_demo_allows_development() -> None:
    require_development("development")


def test_demo_triggers_only_after_expected_thresholds() -> None:
    events = [
        SecurityEvent(**item.model_dump(exclude={"metadata"}))
        for item in demo_events(datetime(2026, 1, 1, tzinfo=UTC))
    ]
    brute = BruteForceRule(10, 120)
    volume = APIVolumeRule(30, 60)
    assert all(
        brute.evaluate(event, events[: index + 1]) is None
        for index, event in enumerate(events[:14])
    )
    finding = brute.evaluate(events[14], events[:15])
    assert finding is not None
    assert len(finding.events) == 10
    assert volume.evaluate(events[43], events[:44]) is None
    assert volume.evaluate(events[44], events) is not None
