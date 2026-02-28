"""Companies API router."""

import os
from uuid import UUID
from pathlib import Path

from fastapi import APIRouter, File, Query, UploadFile

from app.core.config import get_settings
from app.core.database import DbSession
from app.core.dependencies import CurrentUserId
from app.schemas.common import PaginatedResponse
from app.modules.companies.schemas import CompanyCreate, CompanyResponse, CompanyUpdate
from app.modules.companies.service import CompanyService

router = APIRouter(prefix="/companies", tags=["companies"])
ALLOWED_LOGO_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MAX_LOGO_SIZE = 5 * 1024 * 1024  # 5 MB


@router.get("", response_model=PaginatedResponse)
async def list_companies(
    session: DbSession,
    current_user_id: CurrentUserId,
    group_id: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    include_deleted: bool = Query(False),
) -> PaginatedResponse:
    """List companies; filter by group_id if provided. If no group_id, returns all companies (for dropdowns)."""
    svc = CompanyService(session)
    if group_id:
        total = await svc.count_by_group(group_id, include_deleted=include_deleted)
        skip = (page - 1) * page_size
        items = await svc.list_by_group(group_id, skip=skip, limit=page_size, include_deleted=include_deleted)
    else:
        total = await svc.count_all(include_deleted=include_deleted)
        skip = (page - 1) * page_size
        items = await svc.list_all(skip=skip, limit=page_size, include_deleted=include_deleted)
    pages = (total + page_size - 1) // page_size if page_size else 0
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        items=[CompanyResponse.model_validate(c) for c in items],
    )


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> CompanyResponse:
    svc = CompanyService(session)
    company = await svc.get_by_id(company_id)
    return CompanyResponse.model_validate(company)


@router.post("", response_model=CompanyResponse, status_code=201)
async def create_company(
    payload: CompanyCreate,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> CompanyResponse:
    svc = CompanyService(session)
    company = await svc.create(payload)
    return CompanyResponse.model_validate(company)


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: UUID,
    payload: CompanyUpdate,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> CompanyResponse:
    svc = CompanyService(session)
    company = await svc.update(company_id, payload)
    return CompanyResponse.model_validate(company)


@router.delete("/{company_id}", status_code=204)
async def delete_company(
    company_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> None:
    """Soft delete company."""
    svc = CompanyService(session)
    await svc.delete(company_id)


@router.post("/{company_id}/restore", response_model=CompanyResponse)
async def restore_company(
    company_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
) -> CompanyResponse:
    """Restore soft-deleted company."""
    svc = CompanyService(session)
    company = await svc.restore(company_id)
    return CompanyResponse.model_validate(company)


@router.post("/{company_id}/logo", response_model=CompanyResponse)
async def upload_company_logo(
    company_id: UUID,
    session: DbSession,
    current_user_id: CurrentUserId,
    file: UploadFile = File(...),
) -> CompanyResponse:
    """Upload company logo (image file). Replaces logo_url."""
    if not file.filename:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No file")
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_LOGO_EXT:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Allowed: " + ", ".join(ALLOWED_LOGO_EXT))
    content = await file.read()
    if len(content) > MAX_LOGO_SIZE:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="File too large (max 5 MB)")
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    logos_dir = upload_dir / "logos"
    logos_dir.mkdir(parents=True, exist_ok=True)
    filename = f"company_{company_id}{ext}"
    path = logos_dir / filename
    path.write_bytes(content)
    relative_url = f"/uploads/logos/{filename}"
    svc = CompanyService(session)
    company = await svc.get_by_id(company_id)
    company.logo_url = relative_url
    await session.flush()
    await session.refresh(company)
    return CompanyResponse.model_validate(company)
