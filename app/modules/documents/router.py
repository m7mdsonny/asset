"""Documents API router."""

import os
from uuid import UUID, uuid4

from fastapi import APIRouter, File, Query, UploadFile
from fastapi.responses import FileResponse
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.core.activity_logger import log_activity
from app.core.config import get_settings
from app.core.database import DbSession
from app.core.dependencies import CurrentUserId
from app.modules.documents.schemas import DocumentResponse
from app.modules.documents.service import DocumentService
from app.services.pdf_service import render_handover_html

router = APIRouter(prefix="/documents", tags=["documents"])


class HandoverRequest(BaseModel):
    asset_id: UUID
    employee_id: UUID


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    session: DbSession,
    current_user_id: CurrentUserId,
    asset_id: UUID | None = Query(None),
) -> list[DocumentResponse]:
    """List documents; optionally filter by asset_id."""
    svc = DocumentService(session)
    if asset_id is None:
        return []
    items = await svc.list_by_asset(asset_id)
    return [DocumentResponse.model_validate(d) for d in items]


@router.post("/handover", response_model=DocumentResponse, status_code=201)
async def generate_handover(
    body: HandoverRequest,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> DocumentResponse:
    """Generate handover PDF for asset assigned to employee. Saves document record."""
    from fastapi import HTTPException
    svc = DocumentService(session)
    try:
        doc = await svc.generate_handover(
            body.asset_id,
            body.employee_id,
            printed_by=UUID(current_user_id),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    await log_activity(session, "generate_handover", "document", str(doc.id), current_user_id, None)
    return DocumentResponse.model_validate(doc)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> DocumentResponse:
    svc = DocumentService(session)
    doc = await svc.get_by_id(document_id)
    return DocumentResponse.model_validate(doc)


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
):
    """Stream PDF file."""
    svc = DocumentService(session)
    doc = await svc.get_by_id(document_id)
    from pathlib import Path
    path = Path(doc.pdf_path)
    if not path.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="application/pdf", filename=path.name)


@router.get("/{document_id}/preview", response_class=HTMLResponse)
async def preview_handover(
    request: Request,
    document_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
):
    """Return handover as HTML for printing and PDF download. Bilingual AR/EN."""
    svc = DocumentService(session)
    ctx = await svc.get_handover_preview_context(document_id)
    if not ctx:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Document not found or not a handover")
    base = str(request.base_url).rstrip("/")
    download_pdf_url = f"{base}/api/v1/documents/{document_id}/download"
    html = render_handover_html(download_pdf_url=download_pdf_url, **ctx)
    return HTMLResponse(html)


@router.post("/{document_id}/signed-copy", response_model=DocumentResponse)
async def upload_signed_copy(
    document_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
    file: UploadFile = File(...),
) -> DocumentResponse:
    """Upload signed copy PDF for this document."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="PDF file required")
    settings = get_settings()
    os.makedirs(settings.upload_dir, exist_ok=True)
    path = os.path.join(settings.upload_dir, f"signed_{document_id}_{uuid4().hex[:8]}.pdf")
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    svc = DocumentService(session)
    doc = await svc.upload_signed_copy(document_id, path)
    return DocumentResponse.model_validate(doc)
