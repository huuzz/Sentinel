import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class KnowledgeEntryCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    source_url: HttpUrl
    source_type: Literal["authored", "public", "user-authorized"]
    content: str = Field(min_length=20, max_length=20_000)


class KnowledgeEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    source_url: str
    source_type: str
    created_at: datetime
    chunk_count: int


class KnowledgeQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    limit: int = Field(default=3, ge=1, le=5)


class KnowledgeCitation(BaseModel):
    entry_id: uuid.UUID
    chunk_id: uuid.UUID
    title: str
    source_url: str
    excerpt: str = Field(max_length=600)
    relevance: float = Field(ge=-1, le=1)


class KnowledgeAnswer(BaseModel):
    answer: str = Field(max_length=2000)
    citations: list[KnowledgeCitation] = Field(max_length=5)
    provider: str = "local-deterministic"
