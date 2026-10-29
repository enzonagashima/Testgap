"""Standard enumerations for TestGap models and database records."""
from enum import Enum


class ReviewStatus(str, Enum):
    """Status of human review for an example."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class Severity(str, Enum):
    """Severity level of an identified test gap."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class GapStatus(str, Enum):
    """Status of an individual test gap."""
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class SourceType(str, Enum):
    """Origin source of the example data."""
    HUMAN_AUTHORED = "human_authored"
    AI_GENERATED = "ai_generated"
    MUTATION_GENERATED = "mutation_generated"
    PUBLIC_DATASET = "public_dataset"
    IMPORTED = "imported"
    SYNTHETIC = "synthetic"


class AuditIssueSeverity(str, Enum):
    """Severity of a quality rule finding."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
