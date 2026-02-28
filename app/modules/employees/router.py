"""Employees API router."""

from uuid import UUID

from fastapi import APIRouter, Query

from app.core.database import DbSession
from app.core.dependencies import CurrentUserId
from app.schemas.common import PaginatedResponse
from app.modules.employees.schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.modules.employees.service import EmployeeService

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=PaginatedResponse)
async def list_employees(
    session: DbSession,
    current_user_id: CurrentUserId,
    company_id: UUID = Query(...),
    branch_id: UUID | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    include_deleted: bool = Query(False),
) -> PaginatedResponse:
    svc = EmployeeService(session)
    total = await svc.count_by_company(
        company_id, branch_id=branch_id, status=status, include_deleted=include_deleted
    )
    skip = (page - 1) * page_size
    items = await svc.list_by_company(
        company_id,
        branch_id=branch_id,
        status=status,
        skip=skip,
        limit=page_size,
        include_deleted=include_deleted,
    )
    pages = (total + page_size - 1) // page_size if page_size else 0
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        items=[EmployeeResponse.model_validate(e) for e in items],
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> EmployeeResponse:
    svc = EmployeeService(session)
    employee = await svc.get_by_id(employee_id)
    return EmployeeResponse.model_validate(employee)


@router.post("", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    payload: EmployeeCreate,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> EmployeeResponse:
    svc = EmployeeService(session)
    employee = await svc.create(payload)
    return EmployeeResponse.model_validate(employee)


@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: UUID,
    payload: EmployeeUpdate,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> EmployeeResponse:
    svc = EmployeeService(session)
    employee = await svc.update(employee_id, payload)
    return EmployeeResponse.model_validate(employee)


@router.delete("/{employee_id}", status_code=204)
async def delete_employee(
    employee_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> None:
    """Soft delete employee (fails if they have assigned assets)."""
    svc = EmployeeService(session)
    await svc.delete(employee_id)


@router.post("/{employee_id}/restore", response_model=EmployeeResponse)
async def restore_employee(
    employee_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> EmployeeResponse:
    """Restore soft-deleted employee."""
    svc = EmployeeService(session)
    employee = await svc.restore(employee_id)
    return EmployeeResponse.model_validate(employee)
