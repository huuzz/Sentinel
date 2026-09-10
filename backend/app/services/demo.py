"""Synthetic events for the local demo."""

from datetime import datetime, timedelta

from app.schemas.events import SecurityEventCreate

DEMO_SOURCE = "sentinel-portfolio-v1"


def require_development(environment: str) -> None:
    if environment != "development":
        raise ValueError("Demo seeding is allowed only in development")


def demo_events(anchor: datetime) -> list[SecurityEventCreate]:
    events = []
    for index in range(45):
        normal = index < 5
        brute = 5 <= index < 15
        events.append(
            SecurityEventCreate(
                timestamp=anchor + timedelta(seconds=index),
                event_type="authentication" if normal or brute else "api_request",
                source=DEMO_SOURCE,
                outcome="failure" if brute else "success",
                source_ip="198.51.100.201" if brute else "203.0.113.201",
                user_identifier="demo-analyst" if normal else "demo-account",
                endpoint="/login" if normal or brute else "/api/example",
                http_method="POST" if normal or brute else "GET",
                status_code=401 if brute else 200,
                metadata={"seed_index": index, "scenario": "portfolio", "synthetic": True},
                simulated=True,
            )
        )
    return events
