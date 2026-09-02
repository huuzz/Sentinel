import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    actor_user_id: uuid.UUID | None
    action: str
    target_type: str | None
    target_id: str | None
    outcome: str
    details: dict[str, Any]
    created_at: datetime
