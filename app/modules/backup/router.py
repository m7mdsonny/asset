"""Backup and restore API."""

import logging
from datetime import datetime, UTC

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.core.database import DbSession
from app.core.dependencies import CurrentUserId
from app.modules.backup.service import export_backup, import_backup

router = APIRouter(prefix="/backup", tags=["backup"])
logger = logging.getLogger(__name__)


@router.post("/export")
async def create_backup(
    session: DbSession,
    current_user_id: CurrentUserId,
) -> Response:
    """Export full DB as ZIP (JSON per table)."""
    try:
        zip_bytes = await export_backup(session)
    except Exception as e:
        logger.exception("Backup export failed: %s", e)
        raise HTTPException(status_code=500, detail="فشل تصدير النسخة الاحتياطية")
    filename = f"gacms-backup-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}.zip"
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/restore")
async def restore_backup(
    session: DbSession,
    current_user_id: CurrentUserId,
    file: UploadFile = File(..., description="ZIP backup file"),
) -> dict:
    """Restore DB from backup ZIP. Replaces all data."""
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="ZIP file required")
    try:
        zip_bytes = await file.read()
        summary = await import_backup(session, zip_bytes)
    except Exception as e:
        logger.exception("Backup restore failed: %s", e)
        raise HTTPException(status_code=500, detail="فشل استعادة النسخة الاحتياطية")
    return {"message": "Restore completed", **summary}
