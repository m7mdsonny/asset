"""Bulk import API router."""

import os
from uuid import UUID, uuid4

from fastapi import APIRouter, File, Query, UploadFile

from app.core.config import get_settings
from app.core.database import DbSession
from app.core.dependencies import CurrentUserId
from app.modules.bulk_import.schemas import ImportReport
from app.modules.bulk_import.service import BulkImportService

router = APIRouter(prefix="/bulk-import", tags=["bulk-import"])


@router.post("/upload", response_model=ImportReport)
async def upload_and_import(
    session: DbSession,
    current_user_id: CurrentUserId,
    file: UploadFile = File(...),
    company_id: UUID = Query(...),
    branch_id: UUID = Query(...),
) -> ImportReport:
    """Upload Excel and import employees + assets. Sheets: Employees, Assets."""
    settings = get_settings()
    os.makedirs(settings.upload_dir, exist_ok=True)
    path = os.path.join(settings.upload_dir, f"import_{uuid4().hex}_{file.filename or 'upload.xlsx'}")
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    svc = BulkImportService(session)
    emp_created, emp_errors = await svc.import_employees(company_id, branch_id, path)
    asset_created, asset_errors = await svc.import_assets(company_id, branch_id, path)
    return ImportReport(
        employees_created=emp_created,
        employees_errors=emp_errors,
        assets_created=asset_created,
        assets_errors=asset_errors,
    )
