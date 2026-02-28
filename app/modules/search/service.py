"""Global search across assets, employees, companies, branches."""

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.branch import Branch
from app.models.company import Company
from app.models.employee import Employee


class SearchService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def search(
        self,
        q: str,
        company_id: UUID | None = None,
        limit_per_type: int = 20,
    ) -> dict:
        """Search assets, employees, companies, branches by keyword."""
        term = f"%{q.strip()}%" if q else "%"
        assets: list = []
        employees: list = []
        companies: list = []
        branches: list = []

        # Assets: serial_number, brand, model, type
        aq = (
            select(Asset)
            .where(Asset.is_deleted == False)
            .where(
                or_(
                    Asset.serial_number.ilike(term),
                    Asset.brand.ilike(term),
                    Asset.model.ilike(term),
                    Asset.type.ilike(term),
                )
            )
            .limit(limit_per_type)
        )
        if company_id:
            aq = aq.where(Asset.company_id == company_id)
        ar = await self._db.execute(aq)
        for a in ar.scalars().all():
            assets.append({
                "resource_type": "asset",
                "id": a.id,
                "title": f"{a.type} - {a.brand or ''} {a.model or ''} ({a.serial_number or 'N/A'})".strip(),
                "subtitle": a.status,
            })

        # Employees: name, department, job_title
        eq = (
            select(Employee)
            .where(Employee.is_deleted == False)
            .where(
                or_(
                    Employee.name.ilike(term),
                    Employee.department.ilike(term),
                    Employee.job_title.ilike(term),
                )
            )
            .limit(limit_per_type)
        )
        if company_id:
            eq = eq.where(Employee.company_id == company_id)
        er = await self._db.execute(eq)
        for e in er.scalars().all():
            employees.append({
                "resource_type": "employee",
                "id": e.id,
                "title": e.name,
                "subtitle": e.department or e.job_title,
            })

        # Companies: name
        cq = select(Company).where(Company.is_deleted == False).where(Company.name.ilike(term)).limit(limit_per_type)
        if company_id:
            cq = cq.where(Company.id == company_id)
        cr = await self._db.execute(cq)
        for c in cr.scalars().all():
            companies.append({
                "resource_type": "company",
                "id": c.id,
                "title": c.name,
                "subtitle": None,
                "group_id": str(c.group_id),
            })

        # Branches: name, address
        bq = (
            select(Branch)
            .where(Branch.is_deleted == False)
            .where(or_(Branch.name.ilike(term), Branch.address.ilike(term)))
            .limit(limit_per_type)
        )
        if company_id:
            bq = bq.where(Branch.company_id == company_id)
        br = await self._db.execute(bq)
        for b in br.scalars().all():
            branches.append({
                "resource_type": "branch",
                "id": b.id,
                "title": b.name,
                "subtitle": b.address,
                "company_id": str(b.company_id),
            })

        return {
            "query": q,
            "assets": assets,
            "employees": employees,
            "companies": companies,
            "branches": branches,
        }
