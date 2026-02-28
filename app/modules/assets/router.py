"""Assets API router."""

import csv
import io
import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response

from app.core.activity_logger import log_activity
from app.core.database import DbSession
from app.core.dependencies import CurrentUserId
from app.schemas.common import PaginatedResponse
from pydantic import BaseModel

from app.modules.assets.schemas import (
    AssetAssign,
    AssetCreate,
    AssetLogResponse,
    AssetResponse,
    AssetTransfer,
    AssetUpdate,
    MaintenanceRecordResponse,
)
from app.services.qr_service import generate_qr_image
from app.modules.assets.service import AssetService


logger = logging.getLogger(__name__)


class NotesBody(BaseModel):
    notes: str | None = None


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/export")
async def export_assets_csv(
    session: DbSession,
    current_user_id: CurrentUserId,
    company_id: UUID = Query(...),
    branch_id: UUID | None = Query(None),
    status: str | None = Query(None),
):
    """Export assets as CSV (filtered by company/branch/status)."""
    try:
        svc = AssetService(session)
        _, items = await svc.list_filtered(
            company_id=company_id,
            branch_id=branch_id,
            status=status,
            skip=0,
            limit=10000,
        )
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["id", "type", "brand", "model", "serial_number", "status", "current_employee_id", "created_at"])
        for a in items:
            w.writerow([
                str(a.id),
                a.type,
                a.brand or "",
                a.model or "",
                a.serial_number or "",
                a.status,
                str(a.current_employee_id) if a.current_employee_id else "",
                a.created_at.isoformat() if a.created_at else "",
            ])
        return Response(
            content=buf.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=assets.csv"},
        )
    except Exception as e:
        logger.exception("Assets CSV export failed: %s", e)
        raise HTTPException(status_code=500, detail="فشل تصدير الأصول")


@router.get("", response_model=PaginatedResponse)
async def list_assets(
    request: Request,
    session: DbSession,
    current_user_id: CurrentUserId,
    company_id: UUID = Query(...),
    branch_id: UUID | None = Query(None),
    status: str | None = Query(None),
    type: str | None = Query(None, alias="asset_type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    include_deleted: bool = Query(False),
) -> PaginatedResponse:
    svc = AssetService(session)
    total, items = await svc.list_filtered(
        company_id=company_id,
        branch_id=branch_id,
        status=status,
        asset_type=type,
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
        items=[AssetResponse.model_validate(a) for a in items],
    )


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> AssetResponse:
    svc = AssetService(session)
    asset = await svc.get_by_id(asset_id)
    return AssetResponse.model_validate(asset)


@router.get("/{asset_id}/qr", response_class=Response)
async def get_asset_qr(
    asset_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> Response:
    """Return QR code image (PNG) for asset scan URL."""
    svc = AssetService(session)
    await svc.get_by_id(asset_id)
    png_bytes = generate_qr_image(asset_id)
    return Response(content=png_bytes, media_type="image/png")


@router.get("/{asset_id}/timeline", response_model=list[AssetLogResponse])
async def get_asset_timeline(
    asset_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> list[AssetLogResponse]:
    """Full lifecycle history for asset (includes from/to employee names)."""
    svc = AssetService(session)
    await svc.get_by_id(asset_id)  # ensure exists and auth can see
    logs = await svc.get_timeline(asset_id)
    return [
        AssetLogResponse(
            id=l.id,
            asset_id=l.asset_id,
            action_type=l.action_type,
            from_employee_id=l.from_employee_id,
            to_employee_id=l.to_employee_id,
            from_employee_name=l.from_employee.name if l.from_employee else None,
            to_employee_name=l.to_employee.name if l.to_employee else None,
            performed_by_user_id=l.performed_by_user_id,
            ip_address=l.ip_address,
            timestamp=l.timestamp,
            notes=l.notes,
        )
        for l in logs
    ]


@router.get("/{asset_id}/maintenance-records", response_model=list[MaintenanceRecordResponse])
async def get_asset_maintenance_records(
    asset_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> list[MaintenanceRecordResponse]:
    """Maintenance history (send/return with dates) for asset."""
    svc = AssetService(session)
    await svc.get_by_id(asset_id)
    records = await svc.get_maintenance_records(asset_id)
    return [MaintenanceRecordResponse.model_validate(r) for r in records]


@router.post("", response_model=AssetResponse, status_code=201)
async def create_asset(
    request: Request,
    payload: AssetCreate,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> AssetResponse:
    svc = AssetService(session)
    asset = await svc.create(
        payload,
        user_id=UUID(current_user_id),
        ip=_client_ip(request),
    )
    await log_activity(session, "create", "asset", str(asset.id), current_user_id, _client_ip(request))
    return AssetResponse.model_validate(asset)


@router.patch("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    request: Request,
    asset_id: UUID,
    payload: AssetUpdate,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> AssetResponse:
    svc = AssetService(session)
    asset = await svc.update(
        asset_id,
        payload,
        user_id=UUID(current_user_id),
        ip=_client_ip(request),
    )
    return AssetResponse.model_validate(asset)


@router.post("/{asset_id}/assign", response_model=AssetResponse)
async def assign_asset(
    request: Request,
    asset_id: UUID,
    payload: AssetAssign,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> AssetResponse:
    svc = AssetService(session)
    asset = await svc.assign(
        asset_id,
        payload,
        user_id=UUID(current_user_id),
        ip=_client_ip(request),
    )
    return AssetResponse.model_validate(asset)


@router.post("/{asset_id}/transfer", response_model=AssetResponse)
async def transfer_asset(
    request: Request,
    asset_id: UUID,
    payload: AssetTransfer,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> AssetResponse:
    svc = AssetService(session)
    asset = await svc.transfer(
        asset_id,
        payload,
        user_id=UUID(current_user_id),
        ip=_client_ip(request),
    )
    return AssetResponse.model_validate(asset)


@router.post("/{asset_id}/return", response_model=AssetResponse)
async def return_asset(
    request: Request,
    asset_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> AssetResponse:
    svc = AssetService(session)
    asset = await svc.return_asset(
        asset_id,
        user_id=UUID(current_user_id),
        ip=_client_ip(request),
    )
    return AssetResponse.model_validate(asset)


@router.post("/{asset_id}/mark-lost", response_model=AssetResponse)
async def mark_asset_lost(
    request: Request,
    asset_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
    body: NotesBody | None = None,
) -> AssetResponse:
    svc = AssetService(session)
    asset = await svc.mark_lost(
        asset_id,
        notes=body.notes if body else None,
        user_id=UUID(current_user_id),
        ip=_client_ip(request),
    )
    return AssetResponse.model_validate(asset)


@router.post("/{asset_id}/maintenance", response_model=AssetResponse)
async def send_to_maintenance(
    request: Request,
    asset_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
    body: NotesBody | None = None,
) -> AssetResponse:
    svc = AssetService(session)
    asset = await svc.send_to_maintenance(
        asset_id,
        notes=body.notes if body else None,
        user_id=UUID(current_user_id),
        ip=_client_ip(request),
    )
    return AssetResponse.model_validate(asset)


@router.post("/{asset_id}/maintenance/return", response_model=AssetResponse)
async def return_from_maintenance(
    request: Request,
    asset_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> AssetResponse:
    svc = AssetService(session)
    asset = await svc.return_from_maintenance(
        asset_id,
        user_id=UUID(current_user_id),
        ip=_client_ip(request),
    )
    return AssetResponse.model_validate(asset)


@router.post("/{asset_id}/retire", response_model=AssetResponse)
async def retire_asset(
    request: Request,
    asset_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
    body: NotesBody | None = None,
) -> AssetResponse:
    svc = AssetService(session)
    asset = await svc.retire(
        asset_id,
        notes=body.notes if body else None,
        user_id=UUID(current_user_id),
        ip=_client_ip(request),
    )
    return AssetResponse.model_validate(asset)


@router.delete("/{asset_id}", status_code=204)
async def soft_delete_asset(
    request: Request,
    asset_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> None:
    """Soft delete asset (hidden from lists, can be restored)."""
    svc = AssetService(session)
    await svc.soft_delete(
        asset_id,
        user_id=UUID(current_user_id),
        ip=_client_ip(request),
    )
    await log_activity(session, "delete", "asset", str(asset_id), current_user_id, _client_ip(request))


@router.post("/{asset_id}/restore", response_model=AssetResponse)
async def restore_asset(
    request: Request,
    asset_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> AssetResponse:
    """Restore soft-deleted asset."""
    svc = AssetService(session)
    asset = await svc.restore(asset_id)
    await log_activity(session, "restore", "asset", str(asset_id), current_user_id, _client_ip(request))
    return AssetResponse.model_validate(asset)
