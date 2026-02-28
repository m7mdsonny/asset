"""Activity log schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ActivityLogResponse(BaseModel):
    """Activity log entry."""

    id: UUID
    user_id: UUID | None
    action: str
    resource_type: str
    resource_id: str | None
    ip_address: str | None
    details: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}
