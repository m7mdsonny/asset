"""Dashboard / analytics service."""

import calendar
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.company import Company
from app.models.employee import Employee


class DashboardService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def group_dashboard(self, group_id: UUID) -> dict:
        """Totals and distribution by company for a group."""
        companies = (await self._db.execute(
            select(Company).where(Company.group_id == group_id, Company.is_deleted == False)
        )).scalars().all()
        by_company = []
        total_assets = 0
        total_book = Decimal("0")
        lost_count = 0
        for c in companies:
            r = await self._db.execute(
                select(func.count(Asset.id), func.coalesce(func.sum(Asset.current_book_value), 0)).where(Asset.company_id == c.id, Asset.is_deleted == False)
            )
            row = r.one()
            lost_r = (await self._db.execute(select(func.count(Asset.id)).where(Asset.company_id == c.id, Asset.status == "lost", Asset.is_deleted == False))).scalar()
            lost_n = lost_r or 0
            total_assets += row[0] or 0
            total_book += row[1] or 0
            lost_count += lost_n
            by_company.append({
                "company_id": str(c.id),
                "company_name": c.name,
                "asset_count": row[0] or 0,
                "book_value": float(row[1] or 0),
                "lost_count": lost_n,
            })
        return {
            "total_assets": total_assets,
            "total_book_value": float(total_book),
            "lost_count": lost_count,
            "by_company": by_company,
        }

    async def company_dashboard(self, company_id: UUID) -> dict:
        """Company-level: by branch, by department, maintenance, warranty, depreciation."""
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        _, last_day = calendar.monthrange(now.year, now.month)
        end_of_month = start_of_month.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

        total_q = select(func.count(Asset.id), func.coalesce(func.sum(Asset.current_book_value), 0)).where(Asset.company_id == company_id, Asset.is_deleted == False)
        total_row = (await self._db.execute(total_q)).one()
        total_assets = total_row[0] or 0
        total_book = total_row[1] or 0

        by_branch_q = select(Asset.branch_id, func.count(Asset.id)).where(Asset.company_id == company_id, Asset.is_deleted == False).group_by(Asset.branch_id)
        by_branch = [{"branch_id": str(r[0]), "count": r[1]} for r in (await self._db.execute(by_branch_q)).all()]

        by_dept_q = select(Employee.department, func.count(Asset.id)).join(Asset, Asset.current_employee_id == Employee.id).where(Asset.company_id == company_id, Asset.is_deleted == False).group_by(Employee.department)
        by_department = [{"department": r[0] or "Unassigned", "count": r[1]} for r in (await self._db.execute(by_dept_q)).all()]

        maintenance = (await self._db.execute(select(func.count(Asset.id)).where(Asset.company_id == company_id, Asset.status == "maintenance", Asset.is_deleted == False))).scalar() or 0
        lost = (await self._db.execute(select(func.count(Asset.id)).where(Asset.company_id == company_id, Asset.status == "lost", Asset.is_deleted == False))).scalar() or 0
        warranty = (await self._db.execute(
            select(func.count(Asset.id)).where(
                Asset.company_id == company_id,
                Asset.is_deleted == False,
                Asset.warranty_expiry >= start_of_month,
                Asset.warranty_expiry <= end_of_month,
            )
        )).scalar() or 0

        dep_q = select(Asset.depreciation_rate, func.count(Asset.id), func.sum(Asset.current_book_value)).where(Asset.company_id == company_id, Asset.is_deleted == False).group_by(Asset.depreciation_rate)
        dep_rows = (await self._db.execute(dep_q)).all()
        depreciation_summary = {str(r[0]): {"count": r[1], "total_value": float(r[2] or 0)} for r in dep_rows}

        return {
            "total_assets": total_assets,
            "total_book_value": float(total_book),
            "by_branch": by_branch,
            "by_department": by_department,
            "maintenance_count": maintenance,
            "lost_count": lost,
            "warranty_expiring_this_month": warranty,
            "depreciation_summary": depreciation_summary,
        }