"""Asset service: full lifecycle and logging."""

from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import AssetLogAction, AssetStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.models.asset import Asset, AssetLog
from app.models.maintenance_record import MaintenanceRecord
from app.models.employee import Employee
from app.models.company import Company
from app.modules.assets.schemas import (
    AssetAssign,
    AssetCreate,
    AssetTransfer,
    AssetUpdate,
)


class AssetService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _log(
        self,
        asset_id: UUID,
        action_type: str,
        *,
        from_employee_id: UUID | None = None,
        to_employee_id: UUID | None = None,
        performed_by_user_id: UUID | None = None,
        ip_address: str | None = None,
        notes: str | None = None,
    ) -> None:
        entry = AssetLog(
            asset_id=asset_id,
            action_type=action_type,
            from_employee_id=from_employee_id,
            to_employee_id=to_employee_id,
            performed_by_user_id=performed_by_user_id,
            ip_address=ip_address,
            timestamp=datetime.now(UTC),
            notes=notes,
        )
        self._db.add(entry)
        await self._db.flush()

    async def get_by_id(self, asset_id: UUID, include_deleted: bool = False) -> Asset:
        q = (
            select(Asset)
            .where(Asset.id == asset_id)
            .options(
                selectinload(Asset.current_employee),
                selectinload(Asset.company),
            )
        )
        if not include_deleted:
            q = q.where(Asset.is_deleted == False)
        result = await self._db.execute(q)
        asset = result.scalar_one_or_none()
        if not asset:
            raise NotFoundError("Asset not found")
        return asset

    async def list_filtered(
        self,
        company_id: UUID,
        branch_id: UUID | None = None,
        status: str | None = None,
        asset_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> tuple[int, list[Asset]]:
        from sqlalchemy import func
        q = select(Asset).where(Asset.company_id == company_id)
        count_q = select(func.count(Asset.id)).where(Asset.company_id == company_id)
        if not include_deleted:
            q = q.where(Asset.is_deleted == False)
            count_q = count_q.where(Asset.is_deleted == False)
        if branch_id is not None:
            q = q.where(Asset.branch_id == branch_id)
            count_q = count_q.where(Asset.branch_id == branch_id)
        if status is not None:
            q = q.where(Asset.status == status)
            count_q = count_q.where(Asset.status == status)
        if asset_type is not None:
            q = q.where(Asset.type == asset_type)
            count_q = count_q.where(Asset.type == asset_type)
        total = (await self._db.execute(count_q)).scalar() or 0
        result = await self._db.execute(
            q.order_by(Asset.created_at.desc()).offset(skip).limit(limit)
        )
        return total, list(result.scalars().all())

    async def create(self, payload: AssetCreate, *, user_id: UUID | None = None, ip: str | None = None) -> Asset:
        asset = Asset(
            company_id=payload.company_id,
            branch_id=payload.branch_id,
            type=payload.type,
            brand=payload.brand,
            model=payload.model,
            serial_number=payload.serial_number,
            specifications=payload.specifications,
            purchase_value=payload.purchase_value,
            current_book_value=payload.current_book_value or payload.purchase_value,
            depreciation_rate=payload.depreciation_rate,
            status=AssetStatus.ACTIVE.value,
            warranty_expiry=payload.warranty_expiry,
        )
        self._db.add(asset)
        await self._db.flush()
        await self._log(
            asset.id,
            AssetLogAction.CREATED.value,
            performed_by_user_id=user_id,
            ip_address=ip,
        )
        await self._db.refresh(asset)
        return asset

    async def update(
        self,
        asset_id: UUID,
        payload: AssetUpdate,
        *,
        user_id: UUID | None = None,
        ip: str | None = None,
    ) -> Asset:
        asset = await self.get_by_id(asset_id)
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(asset, k, v)
        await self._db.flush()
        await self._log(
            asset_id,
            AssetLogAction.UPDATED.value,
            performed_by_user_id=user_id,
            ip_address=ip,
        )
        await self._db.refresh(asset)
        return asset

    async def assign(
        self,
        asset_id: UUID,
        payload: AssetAssign,
        *,
        user_id: UUID | None = None,
        ip: str | None = None,
    ) -> Asset:
        asset = await self.get_by_id(asset_id)
        if asset.status != AssetStatus.ACTIVE.value:
            raise ConflictError(f"Asset is not active (status: {asset.status})")
        emp_result = await self._db.execute(select(Employee).where(Employee.id == payload.employee_id, Employee.is_deleted == False))
        employee = emp_result.scalar_one_or_none()
        if not employee:
            raise NotFoundError("Employee not found")
        if employee.status != "active":
            raise ConflictError("Cannot assign to inactive employee")
        from_emp = asset.current_employee_id
        asset.current_employee_id = payload.employee_id
        await self._db.flush()
        await self._log(
            asset_id,
            AssetLogAction.ASSIGNED.value,
            from_employee_id=from_emp,
            to_employee_id=payload.employee_id,
            performed_by_user_id=user_id,
            ip_address=ip,
            notes=payload.notes,
        )
        await self._db.refresh(asset)
        return asset

    async def transfer(
        self,
        asset_id: UUID,
        payload: AssetTransfer,
        *,
        user_id: UUID | None = None,
        ip: str | None = None,
    ) -> Asset:
        asset = await self.get_by_id(asset_id)
        if asset.status != AssetStatus.ACTIVE.value:
            raise ConflictError("Asset is not active")
        emp_result = await self._db.execute(select(Employee).where(Employee.id == payload.to_employee_id, Employee.is_deleted == False))
        to_emp = emp_result.scalar_one_or_none()
        if not to_emp:
            raise NotFoundError("Employee not found")
        if to_emp.status != "active":
            raise ConflictError("Cannot transfer to inactive employee")
        from_emp = asset.current_employee_id
        asset.current_employee_id = payload.to_employee_id
        await self._db.flush()
        await self._log(
            asset_id,
            AssetLogAction.TRANSFERRED.value,
            from_employee_id=from_emp,
            to_employee_id=payload.to_employee_id,
            performed_by_user_id=user_id,
            ip_address=ip,
            notes=payload.notes,
        )
        await self._db.refresh(asset)
        return asset

    async def return_asset(
        self,
        asset_id: UUID,
        *,
        user_id: UUID | None = None,
        ip: str | None = None,
    ) -> Asset:
        asset = await self.get_by_id(asset_id)
        from_emp = asset.current_employee_id
        asset.current_employee_id = None
        await self._db.flush()
        await self._log(
            asset_id,
            AssetLogAction.RETURNED.value,
            from_employee_id=from_emp,
            to_employee_id=None,
            performed_by_user_id=user_id,
            ip_address=ip,
        )
        await self._db.refresh(asset)
        return asset

    async def mark_lost(
        self,
        asset_id: UUID,
        notes: str | None = None,
        *,
        user_id: UUID | None = None,
        ip: str | None = None,
    ) -> Asset:
        asset = await self.get_by_id(asset_id)
        from_emp = asset.current_employee_id
        asset.status = AssetStatus.LOST.value
        asset.current_employee_id = None
        await self._db.flush()
        await self._log(
            asset_id,
            AssetLogAction.LOST.value,
            from_employee_id=from_emp,
            performed_by_user_id=user_id,
            ip_address=ip,
            notes=notes,
        )
        await self._db.refresh(asset)
        return asset

    async def send_to_maintenance(
        self,
        asset_id: UUID,
        notes: str | None = None,
        *,
        user_id: UUID | None = None,
        ip: str | None = None,
    ) -> Asset:
        asset = await self.get_by_id(asset_id)
        from_emp = asset.current_employee_id
        asset.status = AssetStatus.MAINTENANCE.value
        asset.current_employee_id = None
        asset.last_maintenance = datetime.now(UTC)
        await self._db.flush()
        await self._log(
            asset_id,
            AssetLogAction.MAINTENANCE_START.value,
            from_employee_id=from_emp,
            performed_by_user_id=user_id,
            ip_address=ip,
            notes=notes,
        )
        rec = MaintenanceRecord(
            asset_id=asset_id,
            record_type="send",
            recorded_at=datetime.now(UTC),
            notes=notes,
            recorded_by_user_id=user_id,
        )
        self._db.add(rec)
        await self._db.flush()
        await self._db.refresh(asset)
        return asset

    async def return_from_maintenance(
        self,
        asset_id: UUID,
        *,
        user_id: UUID | None = None,
        ip: str | None = None,
    ) -> Asset:
        asset = await self.get_by_id(asset_id)
        if asset.status != AssetStatus.MAINTENANCE.value:
            raise ConflictError("Asset is not in maintenance")
        asset.status = AssetStatus.ACTIVE.value
        asset.last_maintenance = datetime.now(UTC)
        await self._db.flush()
        await self._log(
            asset_id,
            AssetLogAction.MAINTENANCE_END.value,
            performed_by_user_id=user_id,
            ip_address=ip,
        )
        rec = MaintenanceRecord(
            asset_id=asset_id,
            record_type="return",
            recorded_at=datetime.now(UTC),
            recorded_by_user_id=user_id,
        )
        self._db.add(rec)
        await self._db.flush()
        await self._db.refresh(asset)
        return asset

    async def retire(
        self,
        asset_id: UUID,
        notes: str | None = None,
        *,
        user_id: UUID | None = None,
        ip: str | None = None,
    ) -> Asset:
        asset = await self.get_by_id(asset_id)
        from_emp = asset.current_employee_id
        asset.status = AssetStatus.RETIRED.value
        asset.current_employee_id = None
        await self._db.flush()
        await self._log(
            asset_id,
            AssetLogAction.RETIRED.value,
            from_employee_id=from_emp,
            performed_by_user_id=user_id,
            ip_address=ip,
            notes=notes,
        )
        await self._db.refresh(asset)
        return asset

    async def get_timeline(self, asset_id: UUID) -> list[AssetLog]:
        """Chronological lifecycle history (newest first), with employee relations loaded."""
        from sqlalchemy.orm import selectinload
        result = await self._db.execute(
            select(AssetLog)
            .where(AssetLog.asset_id == asset_id)
            .options(
                selectinload(AssetLog.from_employee),
                selectinload(AssetLog.to_employee),
            )
            .order_by(AssetLog.timestamp.desc())
        )
        return list(result.scalars().all())

    async def get_maintenance_records(self, asset_id: UUID) -> list[MaintenanceRecord]:
        """Maintenance history for asset (send/return with dates)."""
        result = await self._db.execute(
            select(MaintenanceRecord)
            .where(MaintenanceRecord.asset_id == asset_id)
            .order_by(MaintenanceRecord.recorded_at.desc())
        )
        return list(result.scalars().all())

    async def soft_delete(
        self,
        asset_id: UUID,
        *,
        user_id: UUID | None = None,
        ip: str | None = None,
    ) -> Asset:
        """Soft delete asset (set is_deleted=True)."""
        asset = await self.get_by_id(asset_id)
        asset.is_deleted = True
        asset.deleted_at = datetime.now(UTC)
        await self._db.flush()
        await self._log(
            asset_id,
            "soft_deleted",
            performed_by_user_id=user_id,
            ip_address=ip,
        )
        await self._db.refresh(asset)
        return asset

    async def restore(self, asset_id: UUID) -> Asset:
        """Restore soft-deleted asset."""
        asset = await self.get_by_id(asset_id, include_deleted=True)
        if not asset.is_deleted:
            return asset
        asset.is_deleted = False
        asset.deleted_at = None
        await self._db.flush()
        await self._db.refresh(asset)
        return asset
