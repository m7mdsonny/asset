"""Users API router (CRUD)."""

from uuid import UUID

from fastapi import APIRouter, Query

from app.core.database import DbSession
from app.core.dependencies import CurrentUserId
from app.schemas.common import PaginatedResponse
from app.modules.users.schemas import UserCreate, UserResponse, UserUpdate
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=PaginatedResponse)
async def list_users(
    session: DbSession,
    current_user_id: CurrentUserId,
    company_id: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    include_deleted: bool = Query(False),
) -> PaginatedResponse:
    """List users; filter by company_id if provided."""
    svc = UserService(session)
    total, items = await svc.list_filtered(
        company_id=company_id,
        skip=(page - 1) * page_size,
        limit=page_size,
        include_deleted=include_deleted,
    )
    pages = (total + page_size - 1) // page_size if page_size else 0
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        items=[UserResponse.model_validate(u) for u in items],
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> UserResponse:
    svc = UserService(session)
    user = await svc.get_by_id(user_id)
    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    payload: UserCreate,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> UserResponse:
    svc = UserService(session)
    user = await svc.create(payload)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> UserResponse:
    svc = UserService(session)
    user = await svc.update(user_id, payload)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> None:
    """Soft delete user."""
    svc = UserService(session)
    await svc.delete(user_id)


@router.post("/{user_id}/restore", response_model=UserResponse)
async def restore_user(
    user_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> UserResponse:
    """Restore soft-deleted user."""
    svc = UserService(session)
    user = await svc.restore(user_id)
    return UserResponse.model_validate(user)
