from datetime import UTC, datetime, timedelta


def normal_events() -> list[dict[str, object]]:
    now = datetime.now(UTC)
    return [
        {
            "timestamp": (now + timedelta(seconds=index)).isoformat(),
            "event_type": "authentication",
            "source": "sentinel-demo",
            "outcome": "success",
            "user_identifier": f"demo-user-{index + 1}@example.test",
            "source_ip": f"192.0.2.{10 + index}",
            "metadata": {"scenario": "normal"},
            "simulated": True,
        }
        for index in range(5)
    ]


def brute_force_events() -> list[dict[str, object]]:
    now = datetime.now(UTC)
    return [
        {
            "timestamp": (now + timedelta(seconds=index * 5)).isoformat(),
            "event_type": "authentication",
            "source": "sentinel-demo",
            "outcome": "failure",
            "user_identifier": "target-user@example.test",
            "source_ip": "198.51.100.42",
            "metadata": {"scenario": "brute-force", "attempt": index + 1},
            "simulated": True,
        }
        for index in range(10)
    ]
