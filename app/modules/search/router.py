"""Global search API."""

from uuid import UUID

from fastapi import APIRouter, Query

from app.core.database import DbSession
from app.core.dependencies import CurrentUserId
from app.modules.search.schemas import GlobalSearchResponse, SearchResultItem
from app.modules.search.service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=GlobalSearchResponse)
async def global_search(
    session: DbSession,
    current_user_id: CurrentUserId,
    q: str = Query(..., min_length=1),
    company_id: UUID | None = Query(None),
    limit: int = Query(20, ge=1, le=50),
) -> GlobalSearchResponse:
    """Search across assets, employees, companies, branches."""
    svc = SearchService(session)
    result = await svc.search(q, company_id=company_id, limit_per_type=limit)
    return GlobalSearchResponse(
        query=result["query"],
        assets=[SearchResultItem(**x) for x in result["assets"]],
        employees=[SearchResultItem(**x) for x in result["employees"]],
        companies=[SearchResultItem(**x) for x in result["companies"]],
        branches=[SearchResultItem(**x) for x in result["branches"]],
    )
