"""User service."""

from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.modules.users.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, user_id: UUID, include_deleted: bool = False) -> User:
        q = select(User).where(User.id == user_id)
        if not include_deleted:
            q = q.where(User.is_deleted == False)
        result = await self._db.execute(q)
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User not found")
        return user

    async def get_by_id_str(self, user_id: str, include_deleted: bool = False) -> User:
        try:
            uid = UUID(user_id)
        except ValueError:
            raise NotFoundError("User not found")
        return await self.get_by_id(uid, include_deleted=include_deleted)

    async def get_by_email(self, email: str) -> User | None:
        """Excludes soft-deleted users (for login). Email lookup is case-insensitive."""
        if not (email or "").strip():
            return None
        norm = (email or "").strip().lower()
        result = await self._db.execute(
            select(User).where(
                func.lower(User.email) == norm,
                User.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def list_filtered(
        self,
        company_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> tuple[int, list[User]]:
        from sqlalchemy import func
        q = select(User)
        count_q = select(func.count(User.id))
        if not include_deleted:
            q = q.where(User.is_deleted == False)
            count_q = count_q.where(User.is_deleted == False)
        if company_id is not None:
            q = q.where(User.company_id == company_id)
            count_q = count_q.where(User.company_id == company_id)
        total = (await self._db.execute(count_q)).scalar() or 0
        result = await self._db.execute(q.order_by(User.email).offset(skip).limit(limit))
        return total, list(result.scalars().all())

    async def authenticate(self, email: str, password: str) -> User:
        """Return user if credentials valid; else raise UnauthorizedError."""
        user = await self.get_by_email(email)
        if not user or not user.is_active:
            raise UnauthorizedError("Invalid email or password")
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        return user

    async def create(self, payload: UserCreate) -> User:
        existing = await self.get_by_email(payload.email)
        if existing:
            from app.core.exceptions import ConflictError
            raise ConflictError("User with this email already exists")
        user = User(
            company_id=payload.company_id,
            branch_id=payload.branch_id,
            email=payload.email,
            hashed_password=hash_password(payload.password),
            role=payload.role,
            is_active=True,
        )
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        return user

    async def update(self, user_id: UUID, payload: UserUpdate) -> User:
        user = await self.get_by_id(user_id)
        if payload.email is not None:
            user.email = payload.email
        if payload.password is not None:
            user.hashed_password = hash_password(payload.password)
        if payload.role is not None:
            user.role = payload.role
        if payload.is_active is not None:
            user.is_active = payload.is_active
        await self._db.flush()
        await self._db.refresh(user)
        return user

    def can_access_company(self, user: User, company_id: UUID) -> bool:
        """Check if user can access this company."""
        if user.role == UserRole.GROUP_ADMIN.value:
            return True
        return user.company_id == company_id

    def can_access_branch(self, user: User, branch_id: UUID) -> bool:
        if user.role == UserRole.GROUP_ADMIN.value:
            return True
        if user.role == UserRole.COMPANY_ADMIN.value:
            # Must check branch belongs to user's company (caller loads branch)
            return True
        return user.branch_id == branch_id

    async def delete(self, user_id: UUID) -> None:
        """Soft delete user."""
        user = await self.get_by_id(user_id)
        user.is_deleted = True
        user.deleted_at = datetime.now(UTC)
        await self._db.flush()

    async def restore(self, user_id: UUID) -> User:
        """Restore soft-deleted user."""
        user = await self.get_by_id(user_id, include_deleted=True)
        if not user.is_deleted:
            return user
        user.is_deleted = False
        user.deleted_at = None
        await self._db.flush()
        await self._db.refresh(user)
        return user
