"""Document model (PDF handover, return, maintenance)."""

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import uuid7


class Document(Base):
    """Generated or uploaded document (PDF)."""

    __tablename__ = "documents"

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
    document_type: Mapped[str] = mapped_column(nullable=False, index=True)
    pdf_path: Mapped[str] = mapped_column(nullable=False)
    document_hash: Mapped[str | None] = mapped_column(nullable=True, index=True)
    generated_at: Mapped[datetime] = mapped_column(nullable=False)
    printed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    signed_copy_path: Mapped[str | None] = mapped_column(nullable=True)

    asset: Mapped["Asset"] = relationship(
        "Asset",
        back_populates="documents",
        lazy="selectin",
    )
