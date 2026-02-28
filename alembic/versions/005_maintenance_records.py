"""Add maintenance_records table.

Revision ID: 005
Revises: 004
Create Date: 2025-01-05 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "005"
down_revision: str = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "maintenance_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("record_type", sa.String(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("recorded_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recorded_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index(op.f("ix_maintenance_records_asset_id"), "maintenance_records", ["asset_id"], unique=False)
    op.create_index(op.f("ix_maintenance_records_record_type"), "maintenance_records", ["record_type"], unique=False)
    op.create_index(op.f("ix_maintenance_records_recorded_at"), "maintenance_records", ["recorded_at"], unique=False)
    op.create_index(op.f("ix_maintenance_records_recorded_by_user_id"), "maintenance_records", ["recorded_by_user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_maintenance_records_recorded_by_user_id"), table_name="maintenance_records")
    op.drop_index(op.f("ix_maintenance_records_recorded_at"), table_name="maintenance_records")
    op.drop_index(op.f("ix_maintenance_records_record_type"), table_name="maintenance_records")
    op.drop_index(op.f("ix_maintenance_records_asset_id"), table_name="maintenance_records")
    op.drop_table("maintenance_records")
