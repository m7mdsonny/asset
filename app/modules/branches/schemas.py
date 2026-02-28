"""Branch schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BranchCreate(BaseModel):
    """Create branch payload."""

    company_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    address: str | None = None


class BranchUpdate(BaseModel):
    """Update branch payload."""

    name: str | None = Field(None, min_length=1, max_length=255)
    address: str | None = None


class BranchResponse(BaseModel):
    """Branch in API response."""

    id: UUID
    company_id: UUID
    name: str
    address: str | None
    created_at: datetime
    is_deleted: bool = False

    model_config = {"from_attributes": True}
