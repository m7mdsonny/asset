"""Add missing foreign keys and make assets.branch_id optional.

Revision ID: 004
Revises: 003
Create Date: 2025-01-04 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: str = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- assets: make branch_id nullable and FK ON DELETE SET NULL ---
    op.drop_constraint(
        "assets_branch_id_fkey",
        "assets",
        type_="foreignkey",
    )
    op.alter_column(
        "assets",
        "branch_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )
    op.create_foreign_key(
        "assets_branch_id_fkey",
        "assets",
        "branches",
        ["branch_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # --- asset_logs: add FKs for from_employee_id, to_employee_id, performed_by_user_id ---
    op.create_foreign_key(
        "asset_logs_from_employee_id_fkey",
        "asset_logs",
        "employees",
        ["from_employee_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "asset_logs_to_employee_id_fkey",
        "asset_logs",
        "employees",
        ["to_employee_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "asset_logs_performed_by_user_id_fkey",
        "asset_logs",
        "users",
        ["performed_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_asset_logs_from_employee_id"), "asset_logs", ["from_employee_id"], unique=False)
    op.create_index(op.f("ix_asset_logs_to_employee_id"), "asset_logs", ["to_employee_id"], unique=False)
    op.create_index(op.f("ix_asset_logs_performed_by_user_id"), "asset_logs", ["performed_by_user_id"], unique=False)

    # --- audit_sessions: add FKs for company_id, branch_id, started_by ---
    op.create_foreign_key(
        "audit_sessions_company_id_fkey",
        "audit_sessions",
        "companies",
        ["company_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "audit_sessions_branch_id_fkey",
        "audit_sessions",
        "branches",
        ["branch_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "audit_sessions_started_by_fkey",
        "audit_sessions",
        "users",
        ["started_by"],
        ["id"],
        ondelete="SET NULL",
    )

    # --- audit_scans: add FK for asset_id ---
    op.create_foreign_key(
        "audit_scans_asset_id_fkey",
        "audit_scans",
        "assets",
        ["asset_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(op.f("ix_audit_scans_asset_id"), "audit_scans", ["asset_id"], unique=False)

    # --- documents: add FK for printed_by ---
    op.create_foreign_key(
        "documents_printed_by_fkey",
        "documents",
        "users",
        ["printed_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_documents_printed_by"), "documents", ["printed_by"], unique=False)

    # --- activity_logs: add FK for user_id ---
    op.create_foreign_key(
        "activity_logs_user_id_fkey",
        "activity_logs",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("activity_logs_user_id_fkey", "activity_logs", type_="foreignkey")
    op.drop_index(op.f("ix_documents_printed_by"), table_name="documents")
    op.drop_constraint("documents_printed_by_fkey", "documents", type_="foreignkey")
    op.drop_index(op.f("ix_audit_scans_asset_id"), table_name="audit_scans")
    op.drop_constraint("audit_scans_asset_id_fkey", "audit_scans", type_="foreignkey")
    op.drop_constraint("audit_sessions_started_by_fkey", "audit_sessions", type_="foreignkey")
    op.drop_constraint("audit_sessions_branch_id_fkey", "audit_sessions", type_="foreignkey")
    op.drop_constraint("audit_sessions_company_id_fkey", "audit_sessions", type_="foreignkey")
    op.drop_index(op.f("ix_asset_logs_performed_by_user_id"), table_name="asset_logs")
    op.drop_index(op.f("ix_asset_logs_to_employee_id"), table_name="asset_logs")
    op.drop_index(op.f("ix_asset_logs_from_employee_id"), table_name="asset_logs")
    op.drop_constraint("asset_logs_performed_by_user_id_fkey", "asset_logs", type_="foreignkey")
    op.drop_constraint("asset_logs_to_employee_id_fkey", "asset_logs", type_="foreignkey")
    op.drop_constraint("asset_logs_from_employee_id_fkey", "asset_logs", type_="foreignkey")

    op.drop_constraint("assets_branch_id_fkey", "assets", type_="foreignkey")
    op.alter_column(
        "assets",
        "branch_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    op.create_foreign_key(
        "assets_branch_id_fkey",
        "assets",
        "branches",
        ["branch_id"],
        ["id"],
        ondelete="CASCADE",
    )
