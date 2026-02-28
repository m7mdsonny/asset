"""Structured logging configuration."""

import logging
import sys
from typing import Any

from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Configure application logging."""
    level = logging.DEBUG if settings.debug else logging.INFO
    format_str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


def log_action(
    logger: logging.Logger,
    action: str,
    resource: str,
    resource_id: str | None = None,
    user_id: str | None = None,
    ip: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Log an auditable action."""
    log_extra = {
        "action": action,
        "resource": resource,
        "resource_id": resource_id,
        "user_id": user_id,
        "ip": ip,
        **(extra or {}),
    }
    logger.info("%s | %s | %s", action, resource, resource_id or "-", extra=log_extra)
