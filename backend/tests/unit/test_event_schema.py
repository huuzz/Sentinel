from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.events import SecurityEventCreate


def test_event_normalizes_ip_and_utc() -> None:
    event = SecurityEventCreate(
        timestamp=datetime(2026, 8, 31, 12, tzinfo=UTC),
        event_type="authentication",
        source="test",
        source_ip="2001:0db8::1",
    )
    assert event.source_ip == "2001:db8::1"


def test_event_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError, match="timezone"):
        SecurityEventCreate(
            timestamp=datetime(2026, 8, 31, 12), event_type="authentication", source="test"
        )


def test_event_rejects_oversized_metadata() -> None:
    with pytest.raises(ValidationError, match="16 KiB"):
        SecurityEventCreate(
            event_type="authentication", source="test", metadata={"value": "x" * 17_000}
        )
