"""Activity logs API router."""

from uuid import UUID

from fastapi import APIRouter, Query

from app.core.database import DbSession
from app.core.dependencies import CurrentUserId
from app.schemas.common import PaginatedResponse
from app.modules.logs.schemas import ActivityLogResponse
from app.modules.logs.service import ActivityLogService

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("", response_model=PaginatedResponse)
async def list_activity_logs(
    session: DbSession,
    current_user_id: CurrentUserId,
    user_id: UUID | None = Query(None),
    action: str | None = Query(None),
    resource_type: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse:
    svc = ActivityLogService(session)
    total, items = await svc.list_filtered(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        skip=(page - 1) * page_size,
        limit=page_size,
    )
    pages = (total + page_size - 1) // page_size if page_size else 0
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        items=[ActivityLogResponse.model_validate(e) for e in items],
    )
