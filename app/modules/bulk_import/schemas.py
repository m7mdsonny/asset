"""Bulk import schemas."""

from pydantic import BaseModel


class ImportReport(BaseModel):
    """Result of bulk import."""

    employees_created: int
    employees_errors: list[str]
    assets_created: int
    assets_errors: list[str]
