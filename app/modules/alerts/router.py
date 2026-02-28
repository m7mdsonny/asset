"""Alerts API (health & warranty)."""

from uuid import UUID

from fastapi import APIRouter, Query

from app.core.database import DbSession
from app.core.dependencies import CurrentUserId
from app.modules.alerts.schemas import AlertsResponse, AssetAlertItem
from app.modules.alerts.service import AlertsService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertsResponse)
async def get_alerts(
    session: DbSession,
    current_user_id: CurrentUserId,
    company_id: UUID = Query(...),
    branch_id: UUID | None = Query(None),
) -> AlertsResponse:
    """Assets needing maintenance, warranty expiring this month, and lost."""
    svc = AlertsService(session)
    data = await svc.get_alerts(company_id, branch_id=branch_id)
    return AlertsResponse(
        needing_maintenance=[AssetAlertItem(**x) for x in data["needing_maintenance"]],
        warranty_expiring_this_month=[AssetAlertItem(**x) for x in data["warranty_expiring_this_month"]],
        lost=[AssetAlertItem(**x) for x in data["lost"]],
    )
