"""Branches API router."""

from uuid import UUID

from fastapi import APIRouter, Query

from app.core.database import DbSession
from app.core.dependencies import CurrentUserId
from app.schemas.common import PaginatedResponse
from app.modules.branches.schemas import BranchCreate, BranchResponse, BranchUpdate
from app.modules.branches.service import BranchService

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("", response_model=PaginatedResponse)
async def list_branches(
    session: DbSession,
    current_user_id: CurrentUserId,
    company_id: UUID = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    include_deleted: bool = Query(False),
) -> PaginatedResponse:
    svc = BranchService(session)
    total = await svc.count_by_company(company_id, include_deleted=include_deleted)
    skip = (page - 1) * page_size
    items = await svc.list_by_company(company_id, skip=skip, limit=page_size, include_deleted=include_deleted)
    pages = (total + page_size - 1) // page_size if page_size else 0
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        items=[BranchResponse.model_validate(b) for b in items],
    )


@router.get("/{branch_id}", response_model=BranchResponse)
async def get_branch(
    branch_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> BranchResponse:
    svc = BranchService(session)
    branch = await svc.get_by_id(branch_id)
    return BranchResponse.model_validate(branch)


@router.post("", response_model=BranchResponse, status_code=201)
async def create_branch(
    payload: BranchCreate,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> BranchResponse:
    svc = BranchService(session)
    branch = await svc.create(payload)
    return BranchResponse.model_validate(branch)


@router.patch("/{branch_id}", response_model=BranchResponse)
async def update_branch(
    branch_id: UUID,
    payload: BranchUpdate,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> BranchResponse:
    svc = BranchService(session)
    branch = await svc.update(branch_id, payload)
    return BranchResponse.model_validate(branch)


@router.delete("/{branch_id}", status_code=204)
async def delete_branch(
    branch_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> None:
    """Soft delete branch."""
    svc = BranchService(session)
    await svc.delete(branch_id)


@router.post("/{branch_id}/restore", response_model=BranchResponse)
async def restore_branch(
    branch_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> BranchResponse:
    """Restore soft-deleted branch."""
    svc = BranchService(session)
    branch = await svc.restore(branch_id)
    return BranchResponse.model_validate(branch)
