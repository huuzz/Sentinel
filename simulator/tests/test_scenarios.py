import pytest
from simulator.generator import validate_target
from simulator.scenarios import brute_force_events, normal_events


def test_scenarios_are_synthetic_and_use_reserved_addresses() -> None:
    assert len(normal_events()) == 5
    events = brute_force_events()
    assert len(events) == 10
    assert {event["source_ip"] for event in events} == {"198.51.100.42"}
    assert all(event["simulated"] is True for event in events)


def test_external_targets_are_rejected() -> None:
    with pytest.raises(ValueError, match="local SentinelAI"):
        validate_target("https://example.com")
