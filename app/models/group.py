"""Group model."""

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import SoftDeleteMixin, TimestampMixin, uuid7
from app.core.database import Base


class Group(Base, TimestampMixin, SoftDeleteMixin):
    """Top-level group (owns multiple companies)."""

    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )
    name: Mapped[str] = mapped_column(nullable=False, index=True)

    companies: Mapped[list["Company"]] = relationship(
        "Company",
        back_populates="group",
        lazy="selectin",
    )
