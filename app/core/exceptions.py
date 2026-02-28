"""Application exceptions."""

from fastapi import HTTPException, status


class AppError(HTTPException):
    """Base application HTTP error."""

    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str | None = None,
        headers: dict | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail or "Error", headers=headers)


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ForbiddenError(AppError):
    """Access forbidden."""

    def __init__(self, detail: str = "Access forbidden") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthorizedError(AppError):
    """Unauthorized."""

    def __init__(self, detail: str = "Not authenticated") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ConflictError(AppError):
    """Conflict (e.g. duplicate, business rule)."""

    def __init__(self, detail: str = "Conflict") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ValidationError(AppError):
    """Validation error."""

    def __init__(self, detail: str = "Validation error") -> None:
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
