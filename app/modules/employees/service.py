"""Employee service with responsibility control."""

from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import EmployeeStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.models.employee import Employee
from app.models.asset import Asset
from app.modules.employees.schemas import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, employee_id: UUID, include_deleted: bool = False) -> Employee:
        q = select(Employee).where(Employee.id == employee_id)
        if not include_deleted:
            q = q.where(Employee.is_deleted == False)
        result = await self._db.execute(q)
        emp = result.scalar_one_or_none()
        if not emp:
            raise NotFoundError("Employee not found")
        return emp

    async def list_by_company(
        self,
        company_id: UUID,
        branch_id: UUID | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[Employee]:
        q = select(Employee).where(Employee.company_id == company_id)
        if not include_deleted:
            q = q.where(Employee.is_deleted == False)
        if branch_id is not None:
            q = q.where(Employee.branch_id == branch_id)
        if status is not None:
            q = q.where(Employee.status == status)
        q = q.order_by(Employee.name).offset(skip).limit(limit)
        result = await self._db.execute(q)
        return list(result.scalars().all())

    async def count_by_company(
        self,
        company_id: UUID,
        branch_id: UUID | None = None,
        status: str | None = None,
        include_deleted: bool = False,
    ) -> int:
        from sqlalchemy import func
        q = select(func.count(Employee.id)).where(Employee.company_id == company_id)
        if not include_deleted:
            q = q.where(Employee.is_deleted == False)
        if branch_id is not None:
            q = q.where(Employee.branch_id == branch_id)
        if status is not None:
            q = q.where(Employee.status == status)
        result = await self._db.execute(q)
        return result.scalar() or 0

    async def create(self, payload: EmployeeCreate) -> Employee:
        employee = Employee(
            company_id=payload.company_id,
            branch_id=payload.branch_id,
            name=payload.name,
            national_id=payload.national_id,
            job_title=payload.job_title,
            department=payload.department,
            status=payload.status,
        )
        self._db.add(employee)
        await self._db.flush()
        await self._db.refresh(employee)
        return employee

    async def update(self, employee_id: UUID, payload: EmployeeUpdate) -> Employee:
        employee = await self.get_by_id(employee_id)
        if payload.status is not None and payload.status == EmployeeStatus.RESIGNED.value:
            # Responsibility control: block if assigned assets exist
            result = await self._db.execute(
                select(Asset).where(Asset.current_employee_id == employee_id)
            )
            assigned = list(result.scalars().all())
            if assigned:
                raise ConflictError(
                    f"Cannot set status to resigned: employee has {len(assigned)} assigned asset(s). "
                    "Return or transfer assets first."
                )
        if payload.name is not None:
            employee.name = payload.name
        if payload.national_id is not None:
            employee.national_id = payload.national_id
        if payload.job_title is not None:
            employee.job_title = payload.job_title
        if payload.department is not None:
            employee.department = payload.department
        if payload.branch_id is not None:
            employee.branch_id = payload.branch_id
        if payload.status is not None:
            employee.status = payload.status
        await self._db.flush()
        await self._db.refresh(employee)
        return employee

    async def delete(self, employee_id: UUID) -> None:
        """Soft delete employee. Blocks if they have assigned assets."""
        employee = await self.get_by_id(employee_id)
        result = await self._db.execute(
            select(Asset).where(Asset.current_employee_id == employee_id)
        )
        if result.scalars().first():
            raise ConflictError("Cannot delete employee with assigned assets. Return assets first.")
        employee.is_deleted = True
        employee.deleted_at = datetime.now(UTC)
        await self._db.flush()

    async def restore(self, employee_id: UUID) -> Employee:
        """Restore soft-deleted employee."""
        employee = await self.get_by_id(employee_id, include_deleted=True)
        if not employee.is_deleted:
            return employee
        employee.is_deleted = False
        employee.deleted_at = None
        await self._db.flush()
        await self._db.refresh(employee)
        return employee
