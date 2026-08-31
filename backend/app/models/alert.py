import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin


class AlertSeverity(enum.StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(enum.StrEnum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class Alert(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "alerts"

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity), index=True)
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus), default=AlertStatus.OPEN, index=True
    )
    risk_score: Mapped[float] = mapped_column(Float)
    detection_rule: Mapped[str] = mapped_column(String(100), index=True)
    rule_version: Mapped[str] = mapped_column(String(20))
    deduplication_key: Mapped[str] = mapped_column(String(300), unique=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    evidence: Mapped[list["AlertEvent"]] = relationship(
        back_populates="alert", cascade="all, delete-orphan", lazy="selectin"
    )


class AlertEvent(Base):
    __tablename__ = "alert_events"
    __table_args__ = (UniqueConstraint("alert_id", "event_id"),)

    alert_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("alerts.id", ondelete="CASCADE"), primary_key=True
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("security_events.id", ondelete="CASCADE"), primary_key=True
    )
    alert: Mapped[Alert] = relationship(back_populates="evidence")
