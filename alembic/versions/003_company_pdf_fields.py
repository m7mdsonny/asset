"""Add company fields for PDF branding (address, phone, email, website).

Revision ID: 003
Revises: 002
Create Date: 2025-01-03 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: str = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("address", sa.String(500), nullable=True))
    op.add_column("companies", sa.Column("phone", sa.String(50), nullable=True))
    op.add_column("companies", sa.Column("email", sa.String(255), nullable=True))
    op.add_column("companies", sa.Column("website", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("companies", "website")
    op.drop_column("companies", "email")
    op.drop_column("companies", "phone")
    op.drop_column("companies", "address")
