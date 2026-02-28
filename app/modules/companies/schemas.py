"""Company schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    """Create company payload."""

    group_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    logo_url: str | None = None
    primary_color: str | None = None
    legal_text: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None


class CompanyUpdate(BaseModel):
    """Update company payload."""

    name: str | None = Field(None, min_length=1, max_length=255)
    logo_url: str | None = None
    primary_color: str | None = None
    legal_text: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None


class CompanyResponse(BaseModel):
    """Company in API response."""

    id: UUID
    group_id: UUID
    name: str
    logo_url: str | None
    primary_color: str | None
    legal_text: str | None
    address: str | None
    phone: str | None
    email: str | None
    website: str | None
    created_at: datetime
    is_deleted: bool = False

    model_config = {"from_attributes": True}
