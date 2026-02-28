"""User schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Create user payload."""

    company_id: UUID | None = None  # None for group_admin
    branch_id: UUID | None = None
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(..., pattern="^(group_admin|company_admin|branch_manager|auditor|user)$")


class UserUpdate(BaseModel):
    """Update user payload."""

    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)
    role: str | None = Field(None, pattern="^(group_admin|company_admin|branch_manager|auditor|user)$")
    is_active: bool | None = None


class UserResponse(BaseModel):
    """User in API response (no password)."""

    id: UUID
    company_id: UUID | None
    branch_id: UUID | None
    email: str
    role: str
    is_active: bool
    is_deleted: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class LoginRequest(BaseModel):
    """Login body."""

    email: EmailStr
    password: str
