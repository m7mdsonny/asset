"""Branch model."""

import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, uuid7


class Branch(Base, TimestampMixin, SoftDeleteMixin):
    """Branch under a company."""

    __tablename__ = "branches"

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
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    address: Mapped[str | None] = mapped_column(nullable=True)

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="branches",
        lazy="selectin",
    )
    employees: Mapped[list["Employee"]] = relationship(
        "Employee",
        back_populates="branch",
        lazy="selectin",
    )
    assets: Mapped[list["Asset"]] = relationship(
        "Asset",
        back_populates="branch",
        lazy="selectin",
    )
