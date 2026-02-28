"""Audit schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditSessionCreate(BaseModel):
    """Create audit session."""

    company_id: UUID
    branch_id: UUID | None = None


class AuditSessionResponse(BaseModel):
    """Audit session in API response."""

    id: UUID
    company_id: UUID
    branch_id: UUID | None
    started_by: UUID
    started_at: datetime
    ended_at: datetime | None
    status: str

    model_config = {"from_attributes": True}


class AuditScanPayload(BaseModel):
    """Record a scan (asset_id)."""

    asset_id: UUID


class AuditReportResponse(BaseModel):
    """Audit report: expected vs scanned."""

    audit_id: UUID
    status: str
    total_expected: int
    total_scanned: int
    missing_asset_ids: list[UUID]
    unexpected_asset_ids: list[UUID]
    wrong_branch_asset_ids: list[UUID]
