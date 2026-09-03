from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import AdminUser, ViewerUser
from app.db.session import get_session
from app.models.knowledge import KnowledgeEntry
from app.models.user import AuditLog
from app.rag.local import DeterministicAnswerGenerator, DeterministicEmbeddingProvider
from app.schemas.knowledge import (
    KnowledgeAnswer,
    KnowledgeEntryCreate,
    KnowledgeEntryResponse,
    KnowledgeQuestion,
)
from app.services.knowledge import KnowledgeService

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])
DatabaseSession = Annotated[AsyncSession, Depends(get_session)]


def service(session: AsyncSession) -> KnowledgeService:
    return KnowledgeService(
        session, DeterministicEmbeddingProvider(), DeterministicAnswerGenerator()
    )


def entry_response(entry: KnowledgeEntry) -> KnowledgeEntryResponse:
    return KnowledgeEntryResponse(
        id=entry.id,
        title=entry.title,
        source_url=entry.source_url,
        source_type=entry.source_type,
        created_at=entry.created_at,
        chunk_count=len(entry.chunks),
    )


@router.post("/entries", response_model=KnowledgeEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_entry(
    payload: KnowledgeEntryCreate, session: DatabaseSession, admin: AdminUser
) -> KnowledgeEntryResponse:
    entry = await service(session).create(payload, admin.id)
    session.add(
        AuditLog(
            actor_user_id=admin.id,
            action="knowledge.ingest",
            target_type="knowledge_entry",
            target_id=str(entry.id),
            outcome="SUCCESS",
            details={"source_type": entry.source_type},
        )
    )
    await session.commit()
    return entry_response(entry)


@router.get("/entries", response_model=list[KnowledgeEntryResponse])
async def list_entries(session: DatabaseSession, _: ViewerUser) -> list[KnowledgeEntryResponse]:
    return [entry_response(entry) for entry in await service(session).list()]


@router.post("/ask", response_model=KnowledgeAnswer)
async def ask(
    payload: KnowledgeQuestion, session: DatabaseSession, _: ViewerUser
) -> KnowledgeAnswer:
    return await service(session).answer(payload.question, payload.limit)
