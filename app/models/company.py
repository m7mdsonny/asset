"""Company model."""

import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, uuid7


class Company(Base, TimestampMixin, SoftDeleteMixin):
    """Company under a group."""

    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    logo_url: Mapped[str | None] = mapped_column(nullable=True)
    primary_color: Mapped[str | None] = mapped_column(nullable=True)
    legal_text: Mapped[str | None] = mapped_column(nullable=True)
    address: Mapped[str | None] = mapped_column(nullable=True)
    phone: Mapped[str | None] = mapped_column(nullable=True)
    email: Mapped[str | None] = mapped_column(nullable=True)
    website: Mapped[str | None] = mapped_column(nullable=True)

    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="companies",
        lazy="selectin",
    )
    branches: Mapped[list["Branch"]] = relationship(
        "Branch",
        back_populates="company",
        lazy="selectin",
    )
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="company",
        lazy="selectin",
    )
    employees: Mapped[list["Employee"]] = relationship(
        "Employee",
        back_populates="company",
        lazy="selectin",
    )
    assets: Mapped[list["Asset"]] = relationship(
        "Asset",
        back_populates="company",
        lazy="selectin",
    )
