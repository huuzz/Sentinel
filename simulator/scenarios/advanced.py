from datetime import UTC, datetime, timedelta


def password_spray_events() -> list[dict[str, object]]:
    now = datetime.now(UTC)
    return [
        {
            "timestamp": (now + timedelta(seconds=index * 10)).isoformat(),
            "event_type": "authentication",
            "source": "sentinel-demo",
            "outcome": "failure",
            "user_identifier": f"spray-target-{index + 1}@example.test",
            "source_ip": "203.0.113.50",
            "metadata": {"scenario": "password-spray"},
            "simulated": True,
        }
        for index in range(5)
    ]


def api_volume_events() -> list[dict[str, object]]:
    now = datetime.now(UTC)
    return [
        {
            "timestamp": (now + timedelta(seconds=index)).isoformat(),
            "event_type": "api_request",
            "source": "sentinel-demo",
            "outcome": "success",
            "source_ip": "192.0.2.200",
            "endpoint": "/api/example",
            "http_method": "GET",
            "status_code": 200,
            "metadata": {"scenario": "api-volume"},
            "simulated": True,
        }
        for index in range(30)
    ]


def suspicious_success_events() -> list[dict[str, object]]:
    now = datetime.now(UTC)
    events = [
        {
            "timestamp": (now + timedelta(seconds=index * 10)).isoformat(),
            "event_type": "authentication",
            "source": "sentinel-demo",
            "outcome": "failure",
            "user_identifier": "compromised-user@example.test",
            "source_ip": "198.51.100.77",
            "metadata": {"scenario": "suspicious-success"},
            "simulated": True,
        }
        for index in range(5)
    ]
    events.append(
        {
            "timestamp": (now + timedelta(seconds=55)).isoformat(),
            "event_type": "authentication",
            "source": "sentinel-demo",
            "outcome": "success",
            "user_identifier": "compromised-user@example.test",
            "source_ip": "198.51.100.77",
            "metadata": {"scenario": "suspicious-success"},
            "simulated": True,
        }
    )
    return events
