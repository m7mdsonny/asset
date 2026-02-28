"""Branch service."""

from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.branch import Branch
from app.modules.branches.schemas import BranchCreate, BranchUpdate


class BranchService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, branch_id: UUID, include_deleted: bool = False) -> Branch:
        q = select(Branch).where(Branch.id == branch_id)
        if not include_deleted:
            q = q.where(Branch.is_deleted == False)
        result = await self._db.execute(q)
        branch = result.scalar_one_or_none()
        if not branch:
            raise NotFoundError("Branch not found")
        return branch

    async def list_by_company(
        self,
        company_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[Branch]:
        q = (
            select(Branch)
            .where(Branch.company_id == company_id)
            .order_by(Branch.name)
            .offset(skip)
            .limit(limit)
        )
        if not include_deleted:
            q = q.where(Branch.is_deleted == False)
        result = await self._db.execute(q)
        return list(result.scalars().all())

    async def count_by_company(self, company_id: UUID, include_deleted: bool = False) -> int:
        from sqlalchemy import func
        q = select(func.count(Branch.id)).where(Branch.company_id == company_id)
        if not include_deleted:
            q = q.where(Branch.is_deleted == False)
        result = await self._db.execute(q)
        return result.scalar() or 0

    async def create(self, payload: BranchCreate) -> Branch:
        branch = Branch(
            company_id=payload.company_id,
            name=payload.name,
            address=payload.address,
        )
        self._db.add(branch)
        await self._db.flush()
        await self._db.refresh(branch)
        return branch

    async def update(self, branch_id: UUID, payload: BranchUpdate) -> Branch:
        branch = await self.get_by_id(branch_id)
        if payload.name is not None:
            branch.name = payload.name
        if payload.address is not None:
            branch.address = payload.address
        await self._db.flush()
        await self._db.refresh(branch)
        return branch

    async def delete(self, branch_id: UUID) -> None:
        branch = await self.get_by_id(branch_id)
        branch.is_deleted = True
        branch.deleted_at = datetime.now(UTC)
        await self._db.flush()

    async def restore(self, branch_id: UUID) -> Branch:
        branch = await self.get_by_id(branch_id, include_deleted=True)
        if not branch.is_deleted:
            return branch
        branch.is_deleted = False
        branch.deleted_at = None
        await self._db.flush()
        await self._db.refresh(branch)
        return branch
