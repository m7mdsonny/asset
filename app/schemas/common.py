"""Common schemas: pagination, IDs."""

from uuid import UUID

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Pagination query params."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Generic paginated response."""

    total: int
    page: int
    page_size: int
    pages: int
    items: list


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str
    id: UUID | None = None
