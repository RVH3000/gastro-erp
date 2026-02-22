from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class OutboxEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    event_type: str
    aggregate_type: str
    aggregate_id: str
    payload: dict[str, Any]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: datetime | None = None
