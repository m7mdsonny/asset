"""Document service: generate and store PDFs."""

import hashlib
from datetime import datetime, UTC
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.constants import DocumentType
from app.core.exceptions import NotFoundError
from app.models.asset import Asset
from app.models.company import Company
from app.models.document import Document
from app.models.employee import Employee
from app.services.pdf_service import render_handover_pdf, render_handover_html


class DocumentService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, document_id: UUID) -> Document:
        result = await self._db.execute(select(Document).where(Document.id == document_id))
        doc = result.scalar_one_or_none()
        if not doc:
            raise NotFoundError("Document not found")
        return doc

    async def generate_handover(
        self,
        asset_id: UUID,
        employee_id: UUID,
        *,
        printed_by: UUID | None = None,
    ) -> Document:
        """Generate handover PDF, save to disk, create Document record."""
        asset_result = await self._db.execute(
            select(Asset, Company).join(Company, Asset.company_id == Company.id).where(Asset.id == asset_id)
        )
        asset_row = asset_result.one_or_none()
        if not asset_row:
            raise NotFoundError("Asset not found")
        asset, company = asset_row
        emp_result = await self._db.execute(select(Employee).where(Employee.id == employee_id))
        employee = emp_result.scalar_one_or_none()
        if not employee:
            raise NotFoundError("Employee not found")
        if asset.current_employee_id != employee_id:
            raise ValueError("Asset is not assigned to this employee")

        document_serial = f"HOV-{datetime.now(UTC).strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"
        specs_raw = asset.specifications or {}
        asset_notes = str(specs_raw.get("notes") or "") if isinstance(specs_raw, dict) else ""
        specs = {k: v for k, v in specs_raw.items() if k != "notes"} if isinstance(specs_raw, dict) else {}
        company_logo_url = company.logo_url
        if company_logo_url and company_logo_url.startswith("/uploads/"):
            logo_path = Path(get_settings().upload_dir) / company_logo_url.replace("/uploads/", "").lstrip("/")
            if logo_path.exists():
                company_logo_url = logo_path.as_uri()
        pdf_bytes = render_handover_pdf(
            asset_id=asset.id,
            asset_type=asset.type,
            asset_brand=asset.brand,
            asset_model=asset.model,
            asset_serial=asset.serial_number,
            asset_status=asset.status,
            company_name=company.name,
            company_logo_url=company_logo_url,
            primary_color=company.primary_color,
            legal_text=company.legal_text,
            company_address=company.address,
            company_phone=company.phone,
            company_email=company.email,
            company_website=company.website,
            employee_name=employee.name,
            employee_department=employee.department,
            employee_job_title=employee.job_title,
            document_serial=document_serial,
            asset_specifications=specs,
            asset_notes=asset_notes,
        )
        doc_hash = hashlib.sha256(pdf_bytes).hexdigest()[:64]
        out_dir = Path(get_settings().pdf_output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"handover_{asset_id}_{uuid4().hex[:8]}.pdf"
        pdf_path = str(out_dir / filename)
        Path(pdf_path).write_bytes(pdf_bytes)

        doc = Document(
            asset_id=asset_id,
            document_type=DocumentType.HANDOVER.value,
            pdf_path=pdf_path,
            document_hash=doc_hash,
            generated_at=datetime.now(UTC),
            printed_by=printed_by,
        )
        self._db.add(doc)
        await self._db.flush()
        await self._db.refresh(doc)
        return doc

    async def list_by_asset(self, asset_id: UUID) -> list[Document]:
        result = await self._db.execute(
            select(Document).where(Document.asset_id == asset_id).order_by(Document.generated_at.desc())
        )
        return list(result.scalars().all())

    async def get_handover_preview_context(self, document_id: UUID) -> dict | None:
        """Get context for handover HTML preview. Returns None if doc is not handover or asset has no current employee."""
        doc = await self.get_by_id(document_id)
        if doc.document_type != DocumentType.HANDOVER.value:
            return None
        asset_result = await self._db.execute(
            select(Asset, Company)
            .join(Company, Asset.company_id == Company.id)
            .where(Asset.id == doc.asset_id)
        )
        asset_row = asset_result.one_or_none()
        if not asset_row:
            return None
        asset, company = asset_row
        if not asset.current_employee_id:
            return None
        emp_result = await self._db.execute(select(Employee).where(Employee.id == asset.current_employee_id))
        employee = emp_result.scalar_one_or_none()
        if not employee:
            return None
        document_serial = f"HOV-{doc.generated_at.strftime('%Y%m%d')}-{doc.id.hex[:8].upper()}"
        specs_raw = asset.specifications or {}
        asset_notes = str(specs_raw.get("notes") or "") if isinstance(specs_raw, dict) else ""
        specs = {k: v for k, v in specs_raw.items() if k != "notes"} if isinstance(specs_raw, dict) else {}
        return {
            "asset_id": asset.id,
            "asset_type": asset.type,
            "asset_brand": asset.brand,
            "asset_model": asset.model,
            "asset_serial": asset.serial_number,
            "asset_status": asset.status,
            "company_name": company.name,
            "company_logo_url": company.logo_url,
            "primary_color": company.primary_color,
            "legal_text": company.legal_text,
            "company_address": company.address,
            "company_phone": company.phone,
            "company_email": company.email,
            "company_website": company.website,
            "employee_name": employee.name,
            "employee_department": employee.department,
            "employee_job_title": employee.job_title,
            "document_serial": document_serial,
            "asset_specifications": specs,
            "asset_notes": asset_notes,
        }

    async def upload_signed_copy(self, document_id: UUID, file_path: str) -> Document:
        """Save signed copy path for document (PDF uploaded by user)."""
        doc = await self.get_by_id(document_id)
        doc.signed_copy_path = file_path
        await self._db.flush()
        await self._db.refresh(doc)
        return doc
