"""Groups API router."""

from uuid import UUID

from fastapi import APIRouter, Query, Request

from app.core.activity_logger import log_activity
from app.core.database import DbSession
from app.core.dependencies import CurrentUserId
from app.schemas.common import PaginatedResponse
from app.modules.groups.schemas import GroupCreate, GroupResponse, GroupUpdate
from app.modules.groups.service import GroupService

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("", response_model=PaginatedResponse)
async def list_groups(
    session: DbSession,
    current_user_id: CurrentUserId,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    include_deleted: bool = Query(False),
) -> PaginatedResponse:
    """List all groups (group_admin only in production; here we allow authenticated)."""
    svc = GroupService(session)
    total = await svc.count(include_deleted=include_deleted)
    skip = (page - 1) * page_size
    items = await svc.list_all(skip=skip, limit=page_size, include_deleted=include_deleted)
    pages = (total + page_size - 1) // page_size if page_size else 0
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        items=[GroupResponse.model_validate(g) for g in items],
    )


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> GroupResponse:
    """Get group by id."""
    svc = GroupService(session)
    group = await svc.get_by_id(group_id)
    return GroupResponse.model_validate(group)


@router.post("", response_model=GroupResponse, status_code=201)
async def create_group(
    request: Request,
    payload: GroupCreate,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> GroupResponse:
    """Create a new group."""
    svc = GroupService(session)
    group = await svc.create(payload)
    await log_activity(session, "create", "group", str(group.id), current_user_id, request.client.host if request.client else None)
    return GroupResponse.model_validate(group)


@router.patch("/{group_id}", response_model=GroupResponse)
async def update_group(
    request: Request,
    group_id: UUID,
    payload: GroupUpdate,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> GroupResponse:
    """Update group."""
    svc = GroupService(session)
    group = await svc.update(group_id, payload)
    await log_activity(session, "update", "group", str(group_id), current_user_id, request.client.host if request.client else None)
    return GroupResponse.model_validate(group)


@router.delete("/{group_id}", status_code=204)
async def delete_group(
    request: Request,
    group_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> None:
    """Soft delete group."""
    svc = GroupService(session)
    await svc.delete(group_id)
    await log_activity(session, "delete", "group", str(group_id), current_user_id, request.client.host if request.client else None)


@router.post("/{group_id}/restore", response_model=GroupResponse)
async def restore_group(
    request: Request,
    group_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> GroupResponse:
    """Restore soft-deleted group."""
    svc = GroupService(session)
    group = await svc.restore(group_id)
    await log_activity(session, "restore", "group", str(group_id), current_user_id, request.client.host if request.client else None)
    return GroupResponse.model_validate(group)
