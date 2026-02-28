"""Employee schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EmployeeCreate(BaseModel):
    """Create employee payload."""

    company_id: UUID
    branch_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    national_id: str | None = None
    job_title: str | None = None
    department: str | None = None
    status: str = Field(default="active", pattern="^(active|resigned|terminated)$")


class EmployeeUpdate(BaseModel):
    """Update employee payload."""

    name: str | None = Field(None, min_length=1, max_length=255)
    national_id: str | None = None
    job_title: str | None = None
    department: str | None = None
    branch_id: UUID | None = None
    status: str | None = Field(None, pattern="^(active|resigned|terminated)$")


class EmployeeResponse(BaseModel):
    """Employee in API response."""

    id: UUID
    company_id: UUID
    branch_id: UUID
    name: str
    national_id: str | None
    job_title: str | None
    department: str | None
    status: str
    created_at: datetime
    is_deleted: bool = False

    model_config = {"from_attributes": True}
