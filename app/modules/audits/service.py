"""Audit service: sessions, scans, report."""

from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import AuditSessionStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.models.asset import Asset
from app.models.audit import AuditScan, AuditSession
from app.modules.audits.schemas import AuditSessionCreate


class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_session(self, audit_id: UUID) -> AuditSession:
        result = await self._db.execute(
            select(AuditSession).where(AuditSession.id == audit_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise NotFoundError("Audit session not found")
        return session

    async def list_sessions(
        self,
        company_id: UUID | None = None,
        limit: int = 50,
    ) -> list[AuditSession]:
        q = select(AuditSession).order_by(AuditSession.started_at.desc()).limit(limit)
        if company_id is not None:
            q = q.where(AuditSession.company_id == company_id)
        result = await self._db.execute(q)
        return list(result.scalars().all())

    async def start_session(
        self,
        payload: AuditSessionCreate,
        started_by: UUID,
    ) -> AuditSession:
        audit = AuditSession(
            company_id=payload.company_id,
            branch_id=payload.branch_id,
            started_by=started_by,
            started_at=datetime.now(UTC),
            status=AuditSessionStatus.IN_PROGRESS.value,
        )
        self._db.add(audit)
        await self._db.flush()
        await self._db.refresh(audit)
        return audit

    async def end_session(self, audit_id: UUID) -> AuditSession:
        audit = await self.get_session(audit_id)
        if audit.status != AuditSessionStatus.IN_PROGRESS.value:
            raise ConflictError("Audit is not in progress")
        audit.status = AuditSessionStatus.COMPLETED.value
        audit.ended_at = datetime.now(UTC)
        await self._db.flush()
        await self._db.refresh(audit)
        return audit

    async def record_scan(self, audit_id: UUID, asset_id: UUID) -> AuditScan:
        audit = await self.get_session(audit_id)
        if audit.status != AuditSessionStatus.IN_PROGRESS.value:
            raise ConflictError("Audit is not in progress")
        scan = AuditScan(
            audit_id=audit_id,
            asset_id=asset_id,
            scanned_at=datetime.now(UTC),
        )
        self._db.add(scan)
        await self._db.flush()
        await self._db.refresh(scan)
        return scan

    async def get_report(self, audit_id: UUID) -> dict:
        """Compare expected assets (branch/company) vs scanned. Return missing, unexpected, wrong_branch."""
        audit = await self.get_session(audit_id)
        # Expected: assets that belong to this company (and branch if scope is branch)
        q_expected = select(Asset.id).where(Asset.company_id == audit.company_id, Asset.is_deleted == False)
        if audit.branch_id is not None:
            q_expected = q_expected.where(Asset.branch_id == audit.branch_id)
        expected_ids = set((await self._db.execute(q_expected)).scalars().all())
        # Scanned asset ids
        scans_result = await self._db.execute(
            select(AuditScan.asset_id).where(AuditScan.audit_id == audit_id)
        )
        scanned_ids = set(scans_result.scalars().all())
        missing = list(expected_ids - scanned_ids)
        unexpected = []
        wrong_branch = []
        for aid in scanned_ids:
            if aid not in expected_ids:
                asset_row = (await self._db.execute(select(Asset).where(Asset.id == aid))).scalar_one_or_none()
                if asset_row and asset_row.company_id != audit.company_id:
                    unexpected.append(aid)
                elif asset_row and audit.branch_id is not None and asset_row.branch_id != audit.branch_id:
                    wrong_branch.append(aid)
                else:
                    unexpected.append(aid)
        return {
            "audit_id": audit_id,
            "status": audit.status,
            "total_expected": len(expected_ids),
            "total_scanned": len(scanned_ids),
            "missing_asset_ids": missing,
            "unexpected_asset_ids": unexpected,
            "wrong_branch_asset_ids": wrong_branch,
        }
