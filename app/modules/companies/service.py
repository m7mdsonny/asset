"""Company service."""

from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.company import Company
from app.modules.companies.schemas import CompanyCreate, CompanyUpdate


class CompanyService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, company_id: UUID, include_deleted: bool = False) -> Company:
        q = select(Company).where(Company.id == company_id)
        if not include_deleted:
            q = q.where(Company.is_deleted == False)
        result = await self._db.execute(q)
        company = result.scalar_one_or_none()
        if not company:
            raise NotFoundError("Company not found")
        return company

    async def list_by_group(
        self,
        group_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[Company]:
        q = (
            select(Company)
            .where(Company.group_id == group_id)
            .order_by(Company.name)
            .offset(skip)
            .limit(limit)
        )
        if not include_deleted:
            q = q.where(Company.is_deleted == False)
        result = await self._db.execute(q)
        return list(result.scalars().all())

    async def count_by_group(self, group_id: UUID, include_deleted: bool = False) -> int:
        from sqlalchemy import func
        q = select(func.count(Company.id)).where(Company.group_id == group_id)
        if not include_deleted:
            q = q.where(Company.is_deleted == False)
        result = await self._db.execute(q)
        return result.scalar() or 0

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 500,
        include_deleted: bool = False,
    ) -> list[Company]:
        q = select(Company).order_by(Company.name).offset(skip).limit(limit)
        if not include_deleted:
            q = q.where(Company.is_deleted == False)
        result = await self._db.execute(q)
        return list(result.scalars().all())

    async def count_all(self, include_deleted: bool = False) -> int:
        from sqlalchemy import func
        q = select(func.count(Company.id))
        if not include_deleted:
            q = q.where(Company.is_deleted == False)
        result = await self._db.execute(q)
        return result.scalar() or 0

    async def create(self, payload: CompanyCreate) -> Company:
        company = Company(
            group_id=payload.group_id,
            name=payload.name,
            logo_url=payload.logo_url,
            primary_color=payload.primary_color,
            legal_text=payload.legal_text,
            address=payload.address,
            phone=payload.phone,
            email=payload.email,
            website=payload.website,
        )
        self._db.add(company)
        await self._db.flush()
        await self._db.refresh(company)
        return company

    async def update(self, company_id: UUID, payload: CompanyUpdate) -> Company:
        company = await self.get_by_id(company_id)
        if payload.name is not None:
            company.name = payload.name
        if payload.logo_url is not None:
            company.logo_url = payload.logo_url
        if payload.primary_color is not None:
            company.primary_color = payload.primary_color
        if payload.legal_text is not None:
            company.legal_text = payload.legal_text
        if payload.address is not None:
            company.address = payload.address
        if payload.phone is not None:
            company.phone = payload.phone
        if payload.email is not None:
            company.email = payload.email
        if payload.website is not None:
            company.website = payload.website
        await self._db.flush()
        await self._db.refresh(company)
        return company

    async def delete(self, company_id: UUID) -> None:
        company = await self.get_by_id(company_id)
        company.is_deleted = True
        company.deleted_at = datetime.now(UTC)
        await self._db.flush()

    async def restore(self, company_id: UUID) -> Company:
        company = await self.get_by_id(company_id, include_deleted=True)
        if not company.is_deleted:
            return company
        company.is_deleted = False
        company.deleted_at = None
        await self._db.flush()
        await self._db.refresh(company)
        return company
