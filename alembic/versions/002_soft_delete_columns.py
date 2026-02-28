"""Add soft delete columns (deleted_at, is_deleted).

Revision ID: 002
Revises: 001
Create Date: 2025-01-02 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: str = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for table in ("groups", "companies", "branches", "users", "employees", "assets"):
        op.add_column(table, sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
        op.add_column(table, sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")))
        op.create_index(op.f(f"ix_{table}_is_deleted"), table, ["is_deleted"], unique=False)


def downgrade() -> None:
    for table in ("groups", "companies", "branches", "users", "employees", "assets"):
        op.drop_index(op.f(f"ix_{table}_is_deleted"), table_name=table)
        op.drop_column(table, "is_deleted")
        op.drop_column(table, "deleted_at")
