"""Auth API: login, me."""

import time
from collections import defaultdict

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import DbSession
from app.core.dependencies import CurrentUserId
from app.core.security import create_access_token
from app.modules.users.schemas import LoginRequest, TokenResponse, UserResponse
from app.modules.users.service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])

# Rate limit: max 5 login attempts per IP per 60 seconds
_LOGIN_ATTEMPTS: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT_WINDOW = 60.0
_RATE_LIMIT_MAX = 5


def _client_ip(request: Request) -> str:
    if request.client:
        return request.client.host or "unknown"
    return "unknown"


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    payload: LoginRequest,
    session: DbSession,
) -> TokenResponse:
    """Authenticate and return JWT. Rate limited per IP."""
    ip = _client_ip(request)
    now = time.monotonic()
    # Prune old attempts
    _LOGIN_ATTEMPTS[ip] = [t for t in _LOGIN_ATTEMPTS[ip] if now - t < _RATE_LIMIT_WINDOW]
    if len(_LOGIN_ATTEMPTS[ip]) >= _RATE_LIMIT_MAX:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many login attempts. Try again in a minute."},
        )
    _LOGIN_ATTEMPTS[ip].append(now)

    svc = UserService(session)
    user = await svc.authenticate(payload.email, payload.password)
    settings = get_settings()
    expires_seconds = settings.access_token_expire_minutes * 60
    token = create_access_token(
        str(user.id),
        extra_claims={
            "role": user.role,
            "company_id": str(user.company_id) if user.company_id else None,
            "branch_id": str(user.branch_id) if user.branch_id else None,
        },
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_seconds,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    session: DbSession,
    current_user_id: CurrentUserId,
) -> UserResponse:
    """Get current authenticated user."""
    svc = UserService(session)
    user = await svc.get_by_id_str(current_user_id)
    return UserResponse.model_validate(user)
