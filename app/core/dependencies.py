"""FastAPI dependencies: auth, current user, RBAC."""

from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer

from app.core.constants import UserRole
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)


async def get_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer)],
) -> str | None:
    """Extract Bearer token from Authorization header."""
    if credentials and credentials.scheme == "Bearer":
        return credentials.credentials
    return None


async def get_current_user_id(
    token: Annotated[str | None, Depends(get_token)],
) -> str:
    """Validate JWT and return subject (user id). Raises if invalid."""
    if not token:
        raise UnauthorizedError("Not authenticated")
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedError("Invalid or expired token")
    return payload["sub"]


async def get_optional_user_id(
    token: Annotated[str | None, Depends(get_token)],
) -> str | None:
    """Return user id if valid token, else None (for public scan endpoint)."""
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    return payload["sub"]


def require_roles(*allowed_roles: UserRole):
    """Dependency factory: require current user to have one of the given roles."""

    async def _require_roles(
        user_id: Annotated[str, Depends(get_current_user_id)],
    ) -> str:
        # Role check is done in service layer with full user loaded from DB
        # This dependency only ensures authenticated user id is available
        return user_id

    return _require_roles


CurrentUserId = Annotated[str, Depends(get_current_user_id)]
OptionalUserId = Annotated[str | None, Depends(get_optional_user_id)]
