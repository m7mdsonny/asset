"""Activity log service: append and query."""

from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityLog


class ActivityLogService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def log(
        self,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        user_id: UUID | None = None,
        ip_address: str | None = None,
        details: dict | None = None,
    ) -> ActivityLog:
        entry = ActivityLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            details=details,
            created_at=datetime.now(UTC),
        )
        self._db.add(entry)
        await self._db.flush()
        await self._db.refresh(entry)
        return entry

    async def list_filtered(
        self,
        user_id: UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[int, list[ActivityLog]]:
        from sqlalchemy import func
        q = select(ActivityLog)
        count_q = select(func.count(ActivityLog.id))
        if user_id is not None:
            q = q.where(ActivityLog.user_id == user_id)
            count_q = count_q.where(ActivityLog.user_id == user_id)
        if action is not None:
            q = q.where(ActivityLog.action == action)
            count_q = count_q.where(ActivityLog.action == action)
        if resource_type is not None:
            q = q.where(ActivityLog.resource_type == resource_type)
            count_q = count_q.where(ActivityLog.resource_type == resource_type)
        total = (await self._db.execute(count_q)).scalar() or 0
        result = await self._db.execute(
            q.order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit)
        )
        return total, list(result.scalars().all())
