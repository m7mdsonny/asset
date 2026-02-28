"""Asset and AssetLog models."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, uuid7


class Asset(Base, TimestampMixin, SoftDeleteMixin):
    """Physical IT asset."""

    __tablename__ = "assets"

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
    branch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    type: Mapped[str] = mapped_column(nullable=False, index=True)
    brand: Mapped[str | None] = mapped_column(nullable=True)
    model: Mapped[str | None] = mapped_column(nullable=True)
    serial_number: Mapped[str | None] = mapped_column(nullable=True, index=True)
    specifications: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    purchase_value: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    current_book_value: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    depreciation_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, default="active", index=True)
    current_employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    warranty_expiry: Mapped[datetime | None] = mapped_column(nullable=True)
    last_maintenance: Mapped[datetime | None] = mapped_column(nullable=True)

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="assets",
        lazy="selectin",
    )
    branch: Mapped["Branch | None"] = relationship(
        "Branch",
        back_populates="assets",
        lazy="selectin",
    )
    current_employee: Mapped["Employee | None"] = relationship(
        "Employee",
        back_populates="assigned_assets",
        lazy="selectin",
    )
    logs: Mapped[list["AssetLog"]] = relationship(
        "AssetLog",
        back_populates="asset",
        lazy="selectin",
        order_by="AssetLog.timestamp.desc()",
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="asset",
        lazy="selectin",
    )
    maintenance_records: Mapped[list["MaintenanceRecord"]] = relationship(
        "MaintenanceRecord",
        back_populates="asset",
        lazy="selectin",
        order_by="MaintenanceRecord.recorded_at.desc()",
    )


class AssetLog(Base):
    """Log entry for asset lifecycle events."""

    __tablename__ = "asset_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action_type: Mapped[str] = mapped_column(nullable=False, index=True)
    from_employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    to_employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    performed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    ip_address: Mapped[str | None] = mapped_column(nullable=True)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    asset: Mapped["Asset"] = relationship(
        "Asset",
        back_populates="logs",
        lazy="selectin",
    )
    from_employee: Mapped["Employee | None"] = relationship(
        "Employee",
        foreign_keys=[from_employee_id],
        lazy="selectin",
    )
    to_employee: Mapped["Employee | None"] = relationship(
        "Employee",
        foreign_keys=[to_employee_id],
        lazy="selectin",
    )
