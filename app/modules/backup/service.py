"""Backup and restore service: export/import DB as JSON ZIP."""

import io
import json
import zipfile
from datetime import datetime, UTC
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import (
    ActivityLog,
    Asset,
    AssetLog,
    AuditScan,
    AuditSession,
    Branch,
    Company,
    Document,
    Employee,
    Group,
    MaintenanceRecord,
    User,
)

# Order for restore (respect FK)
RESTORE_ORDER = [
    "groups",
    "companies",
    "branches",
    "users",
    "employees",
    "assets",
    "asset_logs",
    "maintenance_records",
    "documents",
    "audit_sessions",
    "audit_scans",
    "activity_logs",
]

TABLE_MODEL = {
    "groups": Group,
    "companies": Company,
    "branches": Branch,
    "users": User,
    "employees": Employee,
    "assets": Asset,
    "asset_logs": AssetLog,
    "maintenance_records": MaintenanceRecord,
    "documents": Document,
    "audit_sessions": AuditSession,
    "audit_scans": AuditScan,
    "activity_logs": ActivityLog,
}


def _serialize(obj: any) -> any:
    if obj is None:
        return None
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    if hasattr(obj, "__dict__") and not isinstance(obj, (str, dict, list)):
        return str(obj)
    return obj


async def export_backup(session: AsyncSession) -> bytes:
    """Export all tables to a ZIP of JSON files. Returns ZIP bytes."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        meta = {"exported_at": datetime.now(UTC).isoformat(), "tables": []}
        for table_name in RESTORE_ORDER:
            model = TABLE_MODEL.get(table_name)
            if not model:
                continue
            q = select(model).order_by(model.id)
            result = await session.execute(q)
            rows = result.scalars().all()
            items = []
            for obj in rows:
                items.append(
                    {
                        c.key: _serialize(getattr(obj, c.key, None))
                        for c in model.__table__.columns
                    }
                )
            zf.writestr(f"{table_name}.json", json.dumps(items, ensure_ascii=False, indent=0))
            meta["tables"].append({"name": table_name, "count": len(items)})
        zf.writestr("meta.json", json.dumps(meta, ensure_ascii=False))
    buffer.seek(0)
    return buffer.getvalue()


async def import_backup(session: AsyncSession, zip_bytes: bytes) -> dict:
    """Restore from a backup ZIP. Truncates and re-inserts in order. Returns summary."""
    summary = {"restored": {}, "errors": []}
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        for table_name in reversed(RESTORE_ORDER):
            model = TABLE_MODEL.get(table_name)
            if not model:
                continue
            try:
                await session.execute(delete(model))
            except Exception as e:
                summary["errors"].append(f"delete {table_name}: {e}")
                continue

        await session.flush()

        for table_name in RESTORE_ORDER:
            if f"{table_name}.json" not in zf.namelist():
                continue
            model = TABLE_MODEL.get(table_name)
            if not model:
                continue
            try:
                raw = zf.read(f"{table_name}.json")
                items = json.loads(raw.decode("utf-8"))
                for item in items:
                    row = {}
                    for col in model.__table__.columns:
                        v = item.get(col.key)
                        if v is None:
                            row[col.key] = None
                        elif "uuid" in str(col.type).lower() or col.type.python_type == UUID:
                            row[col.key] = UUID(v) if v else None
                        elif "datetime" in str(col.type).lower() or col.type.python_type == datetime:
                            row[col.key] = datetime.fromisoformat(v.replace("Z", "+00:00")) if v else None
                        elif col.type.python_type == Decimal or "numeric" in str(col.type).lower():
                            row[col.key] = Decimal(v) if v is not None else None
                        else:
                            row[col.key] = v
                    session.add(model(**row))
                await session.flush()
                summary["restored"][table_name] = len(items)
            except Exception as e:
                summary["errors"].append(f"{table_name}: {e}")
    return summary
