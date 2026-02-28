"""Audits API router."""

from uuid import UUID

from fastapi import APIRouter, Query
from fastapi.responses import Response

from app.core.database import DbSession
from app.core.dependencies import CurrentUserId
from app.modules.audits.schemas import (
    AuditReportResponse,
    AuditScanPayload,
    AuditSessionCreate,
    AuditSessionResponse,
)
from app.modules.audits.service import AuditService
from app.services.pdf_service import render_audit_report_pdf

router = APIRouter(prefix="/audits", tags=["audits"])


@router.get("", response_model=list[AuditSessionResponse])
async def list_audits(
    session: DbSession,
    current_user_id: CurrentUserId,
    company_id: UUID | None = Query(None),
    limit: int = Query(50, le=200),
) -> list[AuditSessionResponse]:
    """List audit sessions, optionally filtered by company."""
    svc = AuditService(session)
    sessions = await svc.list_sessions(company_id=company_id, limit=limit)
    return [AuditSessionResponse.model_validate(s) for s in sessions]


@router.post("", response_model=AuditSessionResponse, status_code=201)
async def start_audit(
    payload: AuditSessionCreate,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> AuditSessionResponse:
    svc = AuditService(session)
    audit = await svc.start_session(payload, UUID(current_user_id))
    return AuditSessionResponse.model_validate(audit)


@router.post("/{audit_id}/end", response_model=AuditSessionResponse)
async def end_audit(
    audit_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> AuditSessionResponse:
    svc = AuditService(session)
    audit = await svc.end_session(audit_id)
    return AuditSessionResponse.model_validate(audit)


@router.post("/{audit_id}/scan", status_code=201)
async def record_scan(
    audit_id: UUID,
    payload: AuditScanPayload,
    session: DbSession,
    current_user_id: CurrentUserId,
):
    svc = AuditService(session)
    scan = await svc.record_scan(audit_id, payload.asset_id)
    return {"id": scan.id, "asset_id": scan.asset_id, "scanned_at": scan.scanned_at}


@router.get("/{audit_id}/report", response_model=AuditReportResponse)
async def get_audit_report(
    audit_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> AuditReportResponse:
    svc = AuditService(session)
    report = await svc.get_report(audit_id)
    return AuditReportResponse(**report)


@router.get("/{audit_id}/report/pdf")
async def get_audit_report_pdf(
    audit_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> Response:
    """Export audit report as PDF."""
    svc = AuditService(session)
    report = await svc.get_report(audit_id)
    pdf_bytes = render_audit_report_pdf(report)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=audit-report-{audit_id}.pdf"},
    )
