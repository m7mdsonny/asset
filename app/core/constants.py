"""Application-wide constants."""

from enum import Enum


class UserRole(str, Enum):
    """User roles for RBAC."""

    GROUP_ADMIN = "group_admin"
    COMPANY_ADMIN = "company_admin"
    BRANCH_MANAGER = "branch_manager"
    AUDITOR = "auditor"
    USER = "user"


class AssetType(str, Enum):
    """Asset type."""

    LAPTOP = "laptop"
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    MONITOR = "monitor"
    PERIPHERAL = "peripheral"
    OTHER = "other"


class AssetStatus(str, Enum):
    """Asset status."""

    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    LOST = "lost"
    RETIRED = "retired"


class EmployeeStatus(str, Enum):
    """Employee status."""

    ACTIVE = "active"
    RESIGNED = "resigned"
    TERMINATED = "terminated"


class AssetLogAction(str, Enum):
    """Asset log action types."""

    CREATED = "created"
    ASSIGNED = "assigned"
    TRANSFERRED = "transferred"
    RETURNED = "returned"
    MAINTENANCE_START = "maintenance_start"
    MAINTENANCE_END = "maintenance_end"
    LOST = "lost"
    RETIRED = "retired"
    UPDATED = "updated"


class DocumentType(str, Enum):
    """Document type for PDFs."""

    HANDOVER = "handover"
    RETURN = "return"
    MAINTENANCE = "maintenance"


class AuditSessionStatus(str, Enum):
    """Audit session status."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
