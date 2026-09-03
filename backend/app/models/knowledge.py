import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin


class KnowledgeEntry(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "knowledge_entries"

    title: Mapped[str] = mapped_column(String(200))
    source_url: Mapped[str] = mapped_column(String(1000))
    source_type: Mapped[str] = mapped_column(String(30))
    content: Mapped[str] = mapped_column(Text)
    ingested_by_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    chunks: Mapped[list["KnowledgeChunk"]] = relationship(
        back_populates="entry", cascade="all, delete-orphan", lazy="selectin"
    )


class KnowledgeChunk(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "knowledge_chunks"
    __table_args__ = (UniqueConstraint("entry_id", "position"),)

    entry_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("knowledge_entries.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(64))
    entry: Mapped[KnowledgeEntry] = relationship(back_populates="chunks")
