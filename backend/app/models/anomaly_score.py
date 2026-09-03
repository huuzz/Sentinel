import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.security_event import SecurityEvent


class AnomalyScore(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "anomaly_scores"
    __table_args__ = (UniqueConstraint("event_id"),)

    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("security_events.id", ondelete="CASCADE"), unique=True, index=True
    )
    score: Mapped[float] = mapped_column(Float)
    is_anomaly: Mapped[bool] = mapped_column(Boolean)
    model_version: Mapped[str] = mapped_column(String(50))
    feature_schema_version: Mapped[str] = mapped_column(String(20))
    event: Mapped["SecurityEvent"] = relationship(back_populates="anomaly_score")
