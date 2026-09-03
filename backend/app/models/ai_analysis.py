import uuid

from sqlalchemy import Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin


class AIAnalysis(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "ai_analyses"
    __table_args__ = (UniqueConstraint("alert_id"),)

    alert_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("alerts.id", ondelete="CASCADE"), unique=True, index=True
    )
    summary: Mapped[str] = mapped_column(Text)
    likely_attack: Mapped[str] = mapped_column(String(200))
    confidence: Mapped[float] = mapped_column(Float)
    evidence_references: Mapped[list[str]] = mapped_column(JSONB)
    recommended_actions: Mapped[list[str]] = mapped_column(JSONB)
    provider: Mapped[str] = mapped_column(String(80))
    model: Mapped[str] = mapped_column(String(100))
