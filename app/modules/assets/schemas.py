"""Asset schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AssetCreate(BaseModel):
    """Create asset payload."""

    company_id: UUID
    branch_id: UUID
    type: str = Field(..., pattern="^(laptop|mobile|tablet|desktop|monitor|peripheral|printer|other)$")
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    specifications: dict[str, Any] | None = None
    purchase_value: Decimal | None = None
    current_book_value: Decimal | None = None
    depreciation_rate: Decimal | None = None
    warranty_expiry: datetime | None = None


class AssetUpdate(BaseModel):
    """Update asset payload (partial)."""

    type: str | None = Field(None, pattern="^(laptop|mobile|tablet|desktop|monitor|peripheral|printer|other)$")
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    specifications: dict[str, Any] | None = None
    purchase_value: Decimal | None = None
    current_book_value: Decimal | None = None
    depreciation_rate: Decimal | None = None
    warranty_expiry: datetime | None = None
    last_maintenance: datetime | None = None


class AssetAssign(BaseModel):
    """Assign asset to employee."""

    employee_id: UUID
    notes: str | None = None


class AssetTransfer(BaseModel):
    """Transfer asset to another employee."""

    to_employee_id: UUID
    notes: str | None = None


class AssetResponse(BaseModel):
    """Asset in API response."""

    id: UUID
    company_id: UUID
    branch_id: UUID | None
    type: str
    brand: str | None
    model: str | None
    serial_number: str | None
    specifications: dict[str, Any] | None
    purchase_value: Decimal | None
    current_book_value: Decimal | None
    depreciation_rate: Decimal | None
    status: str
    current_employee_id: UUID | None
    warranty_expiry: datetime | None
    last_maintenance: datetime | None
    created_at: datetime
    is_deleted: bool = False

    model_config = {"from_attributes": True}


class AssetLogResponse(BaseModel):
    """Asset log entry in API response."""

    id: UUID
    asset_id: UUID
    action_type: str
    from_employee_id: UUID | None
    to_employee_id: UUID | None
    from_employee_name: str | None = None
    to_employee_name: str | None = None
    performed_by_user_id: UUID | None
    ip_address: str | None
    timestamp: datetime
    notes: str | None

    model_config = {"from_attributes": True}


class MaintenanceRecordResponse(BaseModel):
    """Maintenance record (send/return) in API response."""

    id: UUID
    asset_id: UUID
    record_type: str  # "send" | "return"
    recorded_at: datetime
    notes: str | None
    recorded_by_user_id: UUID | None

    model_config = {"from_attributes": True}


class AssetSummaryPublic(BaseModel):
    """Public scan page: limited asset summary (no sensitive data)."""

    asset_id: UUID
    type: str
    brand: str | None
    model: str | None
    status: str
    company_name: str
    assigned_to: str | None  # Employee name only
    is_lost: bool
