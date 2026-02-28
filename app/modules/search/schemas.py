"""Global search schemas."""

from uuid import UUID

from pydantic import BaseModel


class SearchResultItem(BaseModel):
    """Single search result."""

    resource_type: str  # asset, employee, company, branch
    id: UUID
    title: str
    subtitle: str | None = None
    company_id: str | None = None  # for branches
    group_id: str | None = None   # for companies


class GlobalSearchResponse(BaseModel):
    """Global search response."""

    query: str
    assets: list[SearchResultItem] = []
    employees: list[SearchResultItem] = []
    companies: list[SearchResultItem] = []
    branches: list[SearchResultItem] = []
