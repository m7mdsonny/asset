"""Document schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """Document in API response."""

    id: UUID
    asset_id: UUID
    document_type: str
    pdf_path: str
    document_hash: str | None
    generated_at: datetime
    printed_by: UUID | None
    signed_copy_path: str | None

    model_config = {"from_attributes": True}
