"""Seed script: create default group, company, branch, and admin user."""

import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.group import Group
from app.models.company import Company
from app.models.branch import Branch
from app.models.user import User

DEFAULT_ADMIN_EMAIL = "admin@gacms.example.com"
DEFAULT_ADMIN_PASSWORD = "Admin123!"


async def seed() -> None:
    settings = get_settings()
    async with async_session_factory() as session:
        # Find existing admin user by email (any, including soft-deleted)
        r = await session.execute(select(User).where(User.email == DEFAULT_ADMIN_EMAIL))
        existing = r.scalar_one_or_none()
        if existing:
            # Always reset password and ensure active so login works after seed
            existing.hashed_password = hash_password(DEFAULT_ADMIN_PASSWORD)
            existing.is_active = True
            existing.is_deleted = False
            existing.deleted_at = None
            await session.commit()
            print(f"Admin user updated. Login: {DEFAULT_ADMIN_EMAIL} / {DEFAULT_ADMIN_PASSWORD}")
            return

        group = Group(name="Default Group")
        session.add(group)
        await session.flush()
        company = Company(
            group_id=group.id,
            name="Default Company",
            legal_text="By signing this document, the employee acknowledges receipt and responsibility for the assigned asset.",
        )
        session.add(company)
        await session.flush()
        branch = Branch(company_id=company.id, name="Head Office", address="Main Branch")
        session.add(branch)
        await session.flush()
        user = User(
            company_id=None,
            email=DEFAULT_ADMIN_EMAIL,
            hashed_password=hash_password(DEFAULT_ADMIN_PASSWORD),
            role="group_admin",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        print(f"Seeded: Default Group, Default Company, Head Office branch, {DEFAULT_ADMIN_EMAIL} / {DEFAULT_ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed())
