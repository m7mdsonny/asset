"""Helper to log activity from routers (session, user_id, action, resource, ip)."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.logs.service import ActivityLogService


async def log_activity(
    session: AsyncSession,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    user_id: UUID | str | None = None,
    ip_address: str | None = None,
    details: dict | None = None,
) -> None:
    """Append one entry to activity_logs. Call after successful create/update/delete."""
    uid = UUID(str(user_id)) if user_id else None
    svc = ActivityLogService(session)
    await svc.log(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=uid,
        ip_address=ip_address,
        details=details,
    )
