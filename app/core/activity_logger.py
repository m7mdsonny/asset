"""Helper to log activity from routers (session, user_id, action, resource, ip)."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.logs.service import ActivityLogService


logger = logging.getLogger(__name__)


async def log_activity(
    session: AsyncSession,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    user_id: UUID | str | None = None,
    ip_address: str | None = None,
    details: dict | None = None,
) -> None:
    """Append one entry to activity_logs.

    Logging is best-effort: business operations must not fail if activity logging
    storage is temporarily unavailable or schema is not fully migrated.
    """
    try:
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
    except Exception:
        logger.exception(
            "Failed to write activity log",
            extra={
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "user_id": str(user_id) if user_id else None,
            },
        )
