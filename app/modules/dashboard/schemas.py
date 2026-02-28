"""Dashboard response schemas."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class GroupDashboard(BaseModel):
    """Group-level analytics."""

    total_assets: int
    total_book_value: Decimal | None
    lost_count: int
    by_company: list[dict]


class CompanyDashboard(BaseModel):
    """Company-level analytics."""

    total_assets: int
    total_book_value: Decimal | None
    by_branch: list[dict]
    by_department: list[dict]
    maintenance_count: int
    lost_count: int
    warranty_expiring_this_month: int
    depreciation_summary: dict
