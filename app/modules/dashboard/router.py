"""Dashboard API router."""

from uuid import UUID

from fastapi import APIRouter

from app.core.database import DbSession
from app.core.dependencies import CurrentUserId
from app.modules.dashboard.service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/group/{group_id}")
async def group_dashboard(
    group_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
):
    """Group-level analytics."""
    svc = DashboardService(session)
    return await svc.group_dashboard(group_id)


@router.get("/company/{company_id}")
async def company_dashboard(
    company_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
):
    """Company-level analytics."""
    svc = DashboardService(session)
    return await svc.company_dashboard(company_id)
