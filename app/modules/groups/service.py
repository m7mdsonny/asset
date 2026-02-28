"""Group service: business logic only."""

from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.group import Group
from app.modules.groups.schemas import GroupCreate, GroupUpdate


class GroupService:
    """Group CRUD and queries."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, group_id: UUID, include_deleted: bool = False) -> Group:
        """Get group by id or raise NotFoundError."""
        q = select(Group).where(Group.id == group_id)
        if not include_deleted:
            q = q.where(Group.is_deleted == False)
        result = await self._db.execute(q)
        group = result.scalar_one_or_none()
        if not group:
            raise NotFoundError("Group not found")
        return group

    async def list_all(
        self, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> list[Group]:
        """List all groups (paginated)."""
        q = select(Group).order_by(Group.name).offset(skip).limit(limit)
        if not include_deleted:
            q = q.where(Group.is_deleted == False)
        result = await self._db.execute(q)
        return list(result.scalars().all())

    async def count(self, include_deleted: bool = False) -> int:
        """Total count of groups."""
        from sqlalchemy import func
        q = select(func.count(Group.id))
        if not include_deleted:
            q = q.where(Group.is_deleted == False)
        result = await self._db.execute(q)
        return result.scalar() or 0

    async def create(self, payload: GroupCreate) -> Group:
        """Create a new group."""
        group = Group(name=payload.name)
        self._db.add(group)
        await self._db.flush()
        await self._db.refresh(group)
        return group

    async def update(self, group_id: UUID, payload: GroupUpdate) -> Group:
        """Update group."""
        group = await self.get_by_id(group_id)
        if payload.name is not None:
            group.name = payload.name
        await self._db.flush()
        await self._db.refresh(group)
        return group

    async def delete(self, group_id: UUID) -> None:
        """Soft delete group."""
        group = await self.get_by_id(group_id)
        group.is_deleted = True
        group.deleted_at = datetime.now(UTC)
        await self._db.flush()

    async def restore(self, group_id: UUID) -> Group:
        """Restore soft-deleted group."""
        group = await self.get_by_id(group_id, include_deleted=True)
        if not group.is_deleted:
            return group
        group.is_deleted = False
        group.deleted_at = None
        await self._db.flush()
        await self._db.refresh(group)
        return group
