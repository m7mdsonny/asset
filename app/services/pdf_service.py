"""PDF generation from Jinja2 HTML using WeasyPrint."""

import base64
from pathlib import Path
from uuid import UUID

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from app.core.config import get_settings
from app.services.qr_service import generate_qr_image, get_scan_url


def _template_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "templates"


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_template_dir())),
        autoescape=select_autoescape(["html", "xml"]),
    )


def render_handover_pdf(
    *,
    asset_id: UUID,
    asset_type: str,
    asset_brand: str | None,
    asset_model: str | None,
    asset_serial: str | None,
    asset_status: str,
    company_name: str,
    company_logo_url: str | None,
    primary_color: str | None,
    legal_text: str | None,
    company_address: str | None = None,
    company_phone: str | None = None,
    company_email: str | None = None,
    company_website: str | None = None,
    employee_name: str,
    employee_department: str | None,
    employee_job_title: str | None,
    document_serial: str,
    asset_specifications: dict | None = None,
    asset_notes: str = "",
) -> bytes:
    """Generate handover PDF bytes. QR embedded as base64. Bilingual AR/EN."""
    qr_bytes = generate_qr_image(asset_id)
    qr_base64 = base64.b64encode(qr_bytes).decode("ascii")
    env = _env()
    template = env.get_template("handover.html")
    primary = (primary_color or "#2563eb").strip()
    if not primary.startswith("#"):
        primary = "#2563eb"
    specs = {k: v for k, v in (asset_specifications or {}).items() if k != "notes" and v not in (None, "")}
    html_str = template.render(
        asset_id=str(asset_id),
        asset_type=asset_type,
        asset_brand=asset_brand or "",
        asset_model=asset_model or "",
        asset_serial=asset_serial or "",
        asset_status=asset_status,
        company_name=company_name,
        logo_url=company_logo_url,
        primary_color=primary,
        legal_text=legal_text or "",
        company_address=company_address or "",
        company_phone=company_phone or "",
        company_email=company_email or "",
        company_website=company_website or "",
        employee_name=employee_name,
        employee_department=employee_department or "",
        employee_job_title=employee_job_title or "",
        document_serial=document_serial,
        qr_base64=qr_base64,
        show_toolbar=False,
        download_pdf_url="",
        asset_specifications=specs,
        asset_notes=asset_notes or "",
    )
    font_config = FontConfiguration()
    html_doc = HTML(string=html_str)
    out_dir = Path(get_settings().pdf_output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_bytes = html_doc.write_pdf(font_config=font_config)
    return pdf_bytes


def render_handover_html(
    *,
    asset_id: UUID,
    asset_type: str,
    asset_brand: str | None,
    asset_model: str | None,
    asset_serial: str | None,
    asset_status: str,
    company_name: str,
    company_logo_url: str | None,
    primary_color: str | None,
    legal_text: str | None,
    company_address: str | None = None,
    company_phone: str | None = None,
    company_email: str | None = None,
    company_website: str | None = None,
    employee_name: str,
    employee_department: str | None,
    employee_job_title: str | None,
    document_serial: str,
    download_pdf_url: str,
    asset_specifications: dict | None = None,
    asset_notes: str = "",
) -> str:
    """Render handover as HTML for browser preview (print, PDF download, QR)."""
    qr_bytes = generate_qr_image(asset_id)
    qr_base64 = base64.b64encode(qr_bytes).decode("ascii")
    env = _env()
    template = env.get_template("handover.html")
    primary = (primary_color or "#2563eb").strip()
    if not primary.startswith("#"):
        primary = "#2563eb"
    specs = {k: v for k, v in (asset_specifications or {}).items() if k != "notes" and v not in (None, "")}
    return template.render(
        asset_id=str(asset_id),
        asset_type=asset_type,
        asset_brand=asset_brand or "",
        asset_model=asset_model or "",
        asset_serial=asset_serial or "",
        asset_status=asset_status,
        company_name=company_name,
        logo_url=company_logo_url,
        primary_color=primary,
        legal_text=legal_text or "",
        company_address=company_address or "",
        company_phone=company_phone or "",
        company_email=company_email or "",
        company_website=company_website or "",
        employee_name=employee_name,
        employee_department=employee_department or "",
        employee_job_title=employee_job_title or "",
        document_serial=document_serial,
        qr_base64=qr_base64,
        show_toolbar=True,
        download_pdf_url=download_pdf_url,
        asset_specifications=specs,
        asset_notes=asset_notes or "",
    )


def render_audit_report_pdf(report: dict) -> bytes:
    """Generate audit report PDF from report dict (audit_id, status, total_expected, etc.)."""
    from datetime import datetime, UTC
    env = _env()
    template = env.get_template("audit_report.html")
    html_str = template.render(
        audit_id=str(report.get("audit_id", "")),
        status=report.get("status", ""),
        generated_at=datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        total_expected=report.get("total_expected", 0),
        total_scanned=report.get("total_scanned", 0),
        missing_count=len(report.get("missing_asset_ids", [])),
        unexpected_count=len(report.get("unexpected_asset_ids", [])),
        wrong_branch_count=len(report.get("wrong_branch_asset_ids", [])),
        missing_asset_ids=[str(a) for a in report.get("missing_asset_ids", [])],
        unexpected_asset_ids=[str(a) for a in report.get("unexpected_asset_ids", [])],
        wrong_branch_asset_ids=[str(a) for a in report.get("wrong_branch_asset_ids", [])],
    )
    font_config = FontConfiguration()
    html_doc = HTML(string=html_str)
    return html_doc.write_pdf(font_config=font_config)
