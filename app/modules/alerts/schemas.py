"""Alerts schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AssetAlertItem(BaseModel):
    """Single asset in alerts list."""

    id: UUID
    type: str
    brand: str | None
    model: str | None
    serial_number: str | None
    status: str
    warranty_expiry: datetime | None
    last_maintenance: datetime | None


class AlertsResponse(BaseModel):
    """Alerts for dashboard: maintenance, warranty, lost."""

    needing_maintenance: list[AssetAlertItem]
    warranty_expiring_this_month: list[AssetAlertItem]
    lost: list[AssetAlertItem]
