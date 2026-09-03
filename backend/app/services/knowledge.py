import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.knowledge import KnowledgeChunk, KnowledgeEntry
from app.rag.base import AnswerGenerator, EmbeddingProvider
from app.schemas.knowledge import (
    KnowledgeAnswer,
    KnowledgeCitation,
    KnowledgeEntryCreate,
)


def chunk_text(content: str, size: int = 500) -> list[str]:
    paragraphs = [value.strip() for value in content.splitlines() if value.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        for offset in range(0, len(paragraph), size):
            part = paragraph[offset : offset + size]
            if current and len(current) + len(part) + 1 > size:
                chunks.append(current)
                current = ""
            current = f"{current}\n{part}".strip()
    if current:
        chunks.append(current)
    return chunks[:40]


class KnowledgeService:
    def __init__(
        self, session: AsyncSession, embeddings: EmbeddingProvider, generator: AnswerGenerator
    ) -> None:
        self.session = session
        self.embeddings = embeddings
        self.generator = generator

    async def create(self, payload: KnowledgeEntryCreate, user_id: uuid.UUID) -> KnowledgeEntry:
        entry = KnowledgeEntry(
            title=payload.title,
            source_url=str(payload.source_url),
            source_type=payload.source_type,
            content=payload.content,
            ingested_by_user_id=user_id,
        )
        entry.chunks = [
            KnowledgeChunk(position=index, content=text, embedding=self.embeddings.embed(text))
            for index, text in enumerate(chunk_text(payload.content))
        ]
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def list(self) -> list[KnowledgeEntry]:
        return list(
            await self.session.scalars(
                select(KnowledgeEntry)
                .options(selectinload(KnowledgeEntry.chunks))
                .order_by(KnowledgeEntry.created_at.desc())
                .limit(100)
            )
        )

    async def answer(self, question: str, limit: int) -> KnowledgeAnswer:
        vector = self.embeddings.embed(question)
        distance = KnowledgeChunk.embedding.cosine_distance(vector)
        rows = list(
            await self.session.execute(
                select(KnowledgeChunk, KnowledgeEntry, distance.label("distance"))
                .join(KnowledgeEntry, KnowledgeEntry.id == KnowledgeChunk.entry_id)
                .order_by(distance)
                .limit(limit)
            )
        )
        citations = [
            KnowledgeCitation(
                entry_id=entry.id,
                chunk_id=chunk.id,
                title=entry.title,
                source_url=entry.source_url,
                excerpt=chunk.content[:600],
                relevance=max(-1.0, min(1.0, 1.0 - float(raw_distance))),
            )
            for chunk, entry, raw_distance in rows
        ]
        answer = self.generator.generate(
            question, [(citation.title, citation.excerpt) for citation in citations]
        )
        return KnowledgeAnswer(answer=answer, citations=citations)
