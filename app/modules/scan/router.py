"""Public scan endpoint: show asset summary or lost alert. No auth."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import AssetStatus
from app.core.database import DbSession
from app.models.asset import Asset
from app.models.company import Company
from app.models.employee import Employee
from app.modules.assets.schemas import AssetSummaryPublic

router = APIRouter(prefix="/scan", tags=["scan"])


@router.get("/{asset_id}", response_model=AssetSummaryPublic)
async def get_scan_info(
    asset_id: UUID,
    session: DbSession,
) -> AssetSummaryPublic:
    """Return limited asset summary for QR scan (no sensitive data)."""
    result = await session.execute(
        select(Asset, Company, Employee)
        .join(Company, Asset.company_id == Company.id)
        .outerjoin(Employee, Asset.current_employee_id == Employee.id)
        .where(Asset.id == asset_id, Asset.is_deleted == False)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Asset not found")
    asset, company, employee = row
    return AssetSummaryPublic(
        asset_id=asset.id,
        type=asset.type,
        brand=asset.brand,
        model=asset.model,
        status=asset.status,
        company_name=company.name,
        assigned_to=employee.name if employee else None,
        is_lost=asset.status == AssetStatus.LOST.value,
    )


@router.get("/{asset_id}/page", response_class=HTMLResponse)
async def scan_page(
    asset_id: UUID,
    session: DbSession,
) -> HTMLResponse:
    """Simple HTML page for scan: summary or red LOST alert."""
    result = await session.execute(
        select(Asset, Company, Employee)
        .join(Company, Asset.company_id == Company.id)
        .outerjoin(Employee, Asset.current_employee_id == Employee.id)
        .where(Asset.id == asset_id, Asset.is_deleted == False)
    )
    row = result.one_or_none()
    if not row:
        return HTMLResponse(
            content='<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<link href="https://fonts.googleapis.com/css2?family=Alexandria:wght@400;700&display=swap" rel="stylesheet">'
            '<title>غير موجود</title><body style="font-family:\'Alexandria\',sans-serif;margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#0f172a;color:#fff;text-align:center;">'
            '<h1>الأصل غير موجود</h1></body></html>',
            status_code=404,
        )
    asset, company, employee = row
    is_lost = asset.status == AssetStatus.LOST.value
    type_ar = {"laptop": "لابتوب", "mobile": "موبايل", "tablet": "تابلت", "desktop": "كمبيوتر مكتبي", "monitor": "شاشة", "peripheral": "ملحق", "other": "أخرى"}.get(asset.type, asset.type)
    status_ar = {"active": "نشط", "maintenance": "صيانة", "lost": "مفقود", "retired": "مُستبعَد"}.get(asset.status, asset.status)
    if is_lost:
        html = f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width,initial-scale=1" />
          <link href="https://fonts.googleapis.com/css2?family=Alexandria:wght@400;700&display=swap" rel="stylesheet" />
          <title>جهاز مفقود</title>
          <style>body {{ font-family: 'Alexandria', sans-serif; }}</style>
        </head>
        <body style="margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#b91c1c;color:#fff;text-align:center;padding:1rem;">
        <div>
        <h1 style="font-size:2rem;font-weight:700;">هذا الجهاز مُبلّغ عنه كمفقود</h1>
        <p style="margin-top:1rem;">معرّف الأصل: {asset_id}</p>
        <p>يرجى التواصل مع: {company.name}</p>
        </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html)
    assigned = employee.name if employee else "غير معيّن"
    html = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <link href="https://fonts.googleapis.com/css2?family=Alexandria:wght@400;600;700&display=swap" rel="stylesheet" />
      <title>ملخص الأصل</title>
      <style>body {{ font-family: 'Alexandria', sans-serif; }}</style>
    </head>
    <body style="margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#1e3a5f 0%,#312e81 100%);color:#fff;text-align:center;padding:1rem;">
    <div style="background:rgba(255,255,255,0.08);border-radius:1.5rem;padding:2rem;max-width:400px;">
    <h1 style="font-size:1.75rem;font-weight:700;margin-bottom:1.5rem;">ملخص الأصل</h1>
    <p style="margin:0.5rem 0;"><strong>النوع:</strong> {type_ar} | <strong>العلامة:</strong> {asset.brand or '—'} | <strong>الموديل:</strong> {asset.model or '—'}</p>
    <p style="margin:0.5rem 0;"><strong>الحالة:</strong> {status_ar}</p>
    <p style="margin:0.5rem 0;"><strong>الشركة:</strong> {company.name}</p>
    <p style="margin:0.5rem 0;"><strong>المعيّن له:</strong> {assigned}</p>
    </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
