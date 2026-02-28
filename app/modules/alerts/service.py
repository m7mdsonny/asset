"""Alerts service: assets needing maintenance, warranty expiring, lost."""

import calendar
from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from app.models.asset import Asset


class AlertsService:
    def __init__(self, db) -> None:
        self._db = db

    async def get_alerts(self, company_id: UUID, branch_id: UUID | None = None) -> dict:
        """Return lists of assets: needing maintenance, warranty expiring this month, lost."""
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        _, last_day = calendar.monthrange(now.year, now.month)
        end_of_month = start_of_month.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

        base = select(Asset).where(Asset.company_id == company_id, Asset.is_deleted == False)
        if branch_id is not None:
            base = base.where(Asset.branch_id == branch_id)

        maintenance_q = base.where(Asset.status == "maintenance")
        maintenance = list((await self._db.execute(maintenance_q)).scalars().all())

        warranty_q = base.where(
            Asset.warranty_expiry >= start_of_month,
            Asset.warranty_expiry <= end_of_month,
        )
        warranty = list((await self._db.execute(warranty_q)).scalars().all())

        lost_q = base.where(Asset.status == "lost")
        lost = list((await self._db.execute(lost_q)).scalars().all())

        def to_item(a: Asset) -> dict:
            return {
                "id": a.id,
                "type": a.type,
                "brand": a.brand,
                "model": a.model,
                "serial_number": a.serial_number,
                "status": a.status,
                "warranty_expiry": a.warranty_expiry,
                "last_maintenance": a.last_maintenance,
            }

        return {
            "needing_maintenance": [to_item(a) for a in maintenance],
            "warranty_expiring_this_month": [to_item(a) for a in warranty],
            "lost": [to_item(a) for a in lost],
        }
