"""AnyLover public API."""

from anylover.config import Settings
from anylover.models import (
    Companion,
    ConsentBasis,
    ContextBundle,
    MemoryKind,
    MemoryRecord,
    Sensitivity,
)
from anylover.service import AnyLoverService, MemoryPolicyError

__all__ = [
    "AnyLoverService",
    "Companion",
    "ConsentBasis",
    "ContextBundle",
    "MemoryKind",
    "MemoryPolicyError",
    "MemoryRecord",
    "Sensitivity",
    "Settings",
]

__version__ = "0.1.0"

