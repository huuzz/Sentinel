from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin


class SecurityEvent(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "security_events"
    __table_args__ = (
        Index("ix_security_events_source_ip_timestamp", "source_ip", "timestamp"),
        Index("ix_security_events_event_type_timestamp", "event_type", "timestamp"),
    )

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    source: Mapped[str] = mapped_column(String(100))
    outcome: Mapped[str | None] = mapped_column(String(32), index=True)
    user_identifier: Mapped[str | None] = mapped_column(String(254), index=True)
    source_ip: Mapped[str | None] = mapped_column(String(45), index=True)
    endpoint: Mapped[str | None] = mapped_column(String(500))
    http_method: Mapped[str | None] = mapped_column(String(10))
    status_code: Mapped[int | None] = mapped_column(Integer)
    event_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )
    simulated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
