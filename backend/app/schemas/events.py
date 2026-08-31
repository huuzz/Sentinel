import ipaddress
import json
import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SecurityEventCreate(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_type: str = Field(min_length=1, max_length=64, pattern=r"^[a-z0-9_.-]+$")
    source: str = Field(min_length=1, max_length=100)
    outcome: Literal["success", "failure", "unknown"] | None = None
    user_identifier: str | None = Field(default=None, max_length=254)
    source_ip: str | None = None
    endpoint: str | None = Field(default=None, max_length=500)
    http_method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"] | None = None
    status_code: int | None = Field(default=None, ge=100, le=599)
    metadata: dict[str, Any] = Field(default_factory=dict)
    simulated: bool = False

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp must include a timezone")
        return value.astimezone(UTC)

    @field_validator("source_ip")
    @classmethod
    def validate_ip(cls, value: str | None) -> str | None:
        return str(ipaddress.ip_address(value)) if value else None

    @field_validator("metadata")
    @classmethod
    def bound_metadata(cls, value: dict[str, Any]) -> dict[str, Any]:
        if len(json.dumps(value, default=str).encode()) > 16_384:
            raise ValueError("metadata must be at most 16 KiB")
        return value


class SecurityEventResponse(SecurityEventCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime


class EventIngestResponse(BaseModel):
    event: SecurityEventResponse
    alert_ids: list[uuid.UUID]


class EventListResponse(BaseModel):
    items: list[SecurityEventResponse]
    next_cursor: str | None = None
