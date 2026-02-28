"""Employee model."""

import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, uuid7


class Employee(Base, TimestampMixin, SoftDeleteMixin):
    """Employee (can be assigned assets)."""

    __tablename__ = "employees"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    national_id: Mapped[str | None] = mapped_column(nullable=True, index=True)
    job_title: Mapped[str | None] = mapped_column(nullable=True)
    department: Mapped[str | None] = mapped_column(nullable=True, index=True)
    status: Mapped[str] = mapped_column(nullable=False, default="active", index=True)

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="employees",
        lazy="selectin",
    )
    branch: Mapped["Branch"] = relationship(
        "Branch",
        back_populates="employees",
        lazy="selectin",
    )
    assigned_assets: Mapped[list["Asset"]] = relationship(
        "Asset",
        back_populates="current_employee",
        foreign_keys="Asset.current_employee_id",
        lazy="selectin",
    )
