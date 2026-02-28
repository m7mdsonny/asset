"""Group schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GroupCreate(BaseModel):
    """Create group payload."""

    name: str = Field(..., min_length=1, max_length=255)


class GroupUpdate(BaseModel):
    """Update group payload."""

    name: str | None = Field(None, min_length=1, max_length=255)


class GroupResponse(BaseModel):
    """Group in API response."""

    id: UUID
    name: str
    created_at: datetime
    is_deleted: bool = False

    model_config = {"from_attributes": True}
