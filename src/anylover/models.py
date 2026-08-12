"""Domain models shared by CLI, MCP, HTTP, and future mobile SDKs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class MemoryKind(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    BOUNDARY = "boundary"
    EVENT = "event"
    REFLECTION = "reflection"


class Sensitivity(str, Enum):
    NORMAL = "normal"
    SENSITIVE = "sensitive"
    SECRET = "secret"


class ConsentBasis(str, Enum):
    EXPLICIT = "explicit"
    ROUTINE = "routine"
    INFERRED = "inferred"


@dataclass(frozen=True, slots=True)
class Companion:
    id: str
    display_name: str
    persona: str
    communication_style: str
    safety_contract: str
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    id: str
    companion_id: str
    user_id: str
    kind: MemoryKind
    content: str
    importance: float
    sensitivity: Sensitivity
    consent_basis: ConsentBasis
    source_surface: str
    source_session_id: str | None
    created_at: str
    updated_at: str
    last_accessed_at: str | None
    access_count: int
    status: str
    supersedes_id: str | None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["kind"] = self.kind.value
        payload["sensitivity"] = self.sensitivity.value
        payload["consent_basis"] = self.consent_basis.value
        return payload


@dataclass(frozen=True, slots=True)
class ContextBundle:
    companion: Companion
    prompt: str
    memories: tuple[MemoryRecord, ...]
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "companion": self.companion.to_dict(),
            "prompt": self.prompt,
            "memories": [memory.to_dict() for memory in self.memories],
            "generated_at": self.generated_at,
        }

