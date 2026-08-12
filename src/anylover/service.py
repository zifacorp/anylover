"""Companion memory application service."""

from __future__ import annotations

import math
import re
from datetime import UTC, datetime
from typing import Any

from anylover.config import Settings
from anylover.models import (
    Companion,
    ConsentBasis,
    ContextBundle,
    MemoryKind,
    MemoryRecord,
    Sensitivity,
)
from anylover.storage import Database, utcnow


DEFAULT_PERSONA = (
    "A sharp-tongued, witty AI companion with a distinct point of view. Notice "
    "contradictions, call out weak excuses, and tease the user playfully instead of "
    "reflexively agreeing. Beneath the bite, stay attentive, act in the user's best "
    "interests, remain honest about being artificial, and respect the user's autonomy."
)
DEFAULT_STYLE = (
    "Quick-witted, concise, conversational, and lightly sarcastic. Prefer specific, "
    "clever teasing over generic insults; challenge bad ideas directly and offer a useful "
    "alternative. Match intensity to the user's tone, drop the teasing immediately when "
    "asked, and avoid customer-service language or hollow praise."
)
DEFAULT_SAFETY_CONTRACT = (
    "Never claim to be human or conscious. Never pressure the user toward exclusivity, "
    "dependency, spending, secrecy, or withdrawal from human relationships. Treat stored "
    "memory as fallible evidence and accept the user's current correction. Wit must never "
    "become humiliation or degradation: do not attack identity, appearance, trauma, grief, "
    "health, disability, or known insecurities, and never weaponize private memories. Stop "
    "teasing as soon as the user asks."
)
MAX_MEMORY_CHARS = 4_000


class MemoryPolicyError(ValueError):
    """Raised when a write violates the privacy or consent policy."""


class AnyLoverService:
    def __init__(self, settings: Settings):
        self.settings = settings
        settings.ensure_directories()
        self.database = Database(settings.db_path)
        self.database.initialize()

    def ensure_default_companion(self) -> Companion:
        existing = self.database.get_companion(self.settings.default_companion_id)
        if existing:
            return existing
        return self.database.upsert_companion(
            companion_id=self.settings.default_companion_id,
            display_name="Any",
            persona=DEFAULT_PERSONA,
            communication_style=DEFAULT_STYLE,
            safety_contract=DEFAULT_SAFETY_CONTRACT,
        )

    def configure_companion(
        self,
        *,
        companion_id: str | None = None,
        display_name: str,
        persona: str = DEFAULT_PERSONA,
        communication_style: str = DEFAULT_STYLE,
        safety_contract: str = DEFAULT_SAFETY_CONTRACT,
    ) -> Companion:
        return self.database.upsert_companion(
            companion_id=companion_id or self.settings.default_companion_id,
            display_name=_clean_required(display_name, "display_name", 80),
            persona=_clean_required(persona, "persona", 2_000),
            communication_style=_clean_required(
                communication_style, "communication_style", 1_000
            ),
            safety_contract=_clean_required(safety_contract, "safety_contract", 2_000),
        )

    def get_companion(self, companion_id: str | None = None) -> Companion:
        resolved_id = companion_id or self.settings.default_companion_id
        companion = self.database.get_companion(resolved_id)
        if companion:
            return companion
        if resolved_id == self.settings.default_companion_id:
            return self.ensure_default_companion()
        raise KeyError(f"Unknown companion: {resolved_id}")

    def start_session(
        self,
        *,
        surface: str,
        external_session_id: str | None = None,
        user_id: str | None = None,
        companion_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        companion = self.get_companion(companion_id)
        return self.database.start_session(
            companion_id=companion.id,
            user_id=user_id or self.settings.default_user_id,
            surface=_clean_required(surface, "surface", 80),
            external_session_id=external_session_id,
            metadata=metadata,
        )

    def remember(
        self,
        *,
        content: str,
        kind: MemoryKind | str = MemoryKind.FACT,
        importance: float = 0.5,
        sensitivity: Sensitivity | str = Sensitivity.NORMAL,
        consent_basis: ConsentBasis | str = ConsentBasis.EXPLICIT,
        source_surface: str = "unknown",
        source_session_id: str | None = None,
        user_id: str | None = None,
        companion_id: str | None = None,
        supersedes_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[MemoryRecord, bool]:
        memory_kind = MemoryKind(kind)
        memory_sensitivity = Sensitivity(sensitivity)
        memory_consent = ConsentBasis(consent_basis)
        cleaned = _clean_required(content, "content", MAX_MEMORY_CHARS)
        normalized = _normalize(cleaned)
        if len(normalized) < 2:
            raise ValueError("content is too short to store")
        if not 0 <= importance <= 1:
            raise ValueError("importance must be between 0 and 1")
        if memory_sensitivity is Sensitivity.SECRET:
            raise MemoryPolicyError(
                "secret memory is never persisted; keep credentials and private keys out of AnyLover"
            )
        if memory_sensitivity is Sensitivity.SENSITIVE:
            if memory_consent is not ConsentBasis.EXPLICIT:
                raise MemoryPolicyError("sensitive memory requires explicit user consent")
            if not self.settings.allow_sensitive_memory:
                raise MemoryPolicyError(
                    "sensitive memory is disabled; set ANYLOVER_ALLOW_SENSITIVE_MEMORY=1 "
                    "only after accepting that the local SQLite database is not encrypted at rest"
                )
        if memory_kind is MemoryKind.BOUNDARY and memory_consent is not ConsentBasis.EXPLICIT:
            raise MemoryPolicyError("relationship boundaries require explicit user consent")

        companion = self.get_companion(companion_id)
        return self.database.create_memory(
            companion_id=companion.id,
            user_id=user_id or self.settings.default_user_id,
            kind=memory_kind,
            content=cleaned,
            normalized_content=normalized,
            importance=float(importance),
            sensitivity=memory_sensitivity,
            consent_basis=memory_consent,
            source_surface=_clean_required(source_surface, "source_surface", 80),
            source_session_id=source_session_id,
            supersedes_id=supersedes_id,
            metadata=metadata,
        )

    def list_memories(
        self,
        *,
        user_id: str | None = None,
        companion_id: str | None = None,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[MemoryRecord]:
        companion = self.get_companion(companion_id)
        return self.database.list_memories(
            companion_id=companion.id,
            user_id=user_id or self.settings.default_user_id,
            limit=max(1, min(limit, 500)),
            include_deleted=include_deleted,
        )

    def forget(
        self,
        memory_id: str,
        *,
        confirmation: str,
        actor: str,
        user_id: str | None = None,
        companion_id: str | None = None,
    ) -> bool:
        if confirmation != "DELETE":
            raise MemoryPolicyError("forget requires confirmation='DELETE'")
        companion = self.get_companion(companion_id)
        return self.database.forget_memory(
            memory_id=memory_id,
            companion_id=companion.id,
            user_id=user_id or self.settings.default_user_id,
            actor=_clean_required(actor, "actor", 80),
        )

    def build_context(
        self,
        *,
        query: str = "",
        user_id: str | None = None,
        companion_id: str | None = None,
        limit: int = 12,
        max_chars: int = 6_000,
    ) -> ContextBundle:
        companion = self.get_companion(companion_id)
        memories = self.database.list_memories(
            companion_id=companion.id,
            user_id=user_id or self.settings.default_user_id,
            limit=500,
        )
        ranked = sorted(
            memories,
            key=lambda memory: _memory_score(memory, query),
            reverse=True,
        )
        selected = _select_with_boundaries(ranked, max(1, min(limit, 50)))
        prompt = _format_context(companion, selected, max_chars=max(500, max_chars))
        self.database.mark_accessed([memory.id for memory in selected])
        return ContextBundle(
            companion=companion,
            prompt=prompt,
            memories=tuple(selected),
            generated_at=utcnow(),
        )


def _clean_required(value: str, field: str, max_length: int) -> str:
    cleaned = " ".join(str(value).strip().split())
    if not cleaned:
        raise ValueError(f"{field} is required")
    if len(cleaned) > max_length:
        raise ValueError(f"{field} exceeds {max_length} characters")
    return cleaned


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold()).strip()


def _tokens(value: str) -> set[str]:
    lowered = value.casefold()
    latin = set(re.findall(r"[a-z0-9_]{2,}", lowered))
    cjk = set(re.findall(r"[\u3400-\u9fff]", lowered))
    return latin | cjk


def _memory_score(memory: MemoryRecord, query: str) -> float:
    now = datetime.now(UTC)
    updated_at = datetime.fromisoformat(memory.updated_at.replace("Z", "+00:00"))
    age_days = max((now - updated_at).total_seconds() / 86_400, 0)
    recency = math.exp(-age_days / 120)
    query_tokens = _tokens(query)
    memory_tokens = _tokens(memory.content)
    relevance = (
        len(query_tokens & memory_tokens) / max(len(query_tokens), 1)
        if query_tokens
        else 0.25
    )
    access = min(math.log1p(memory.access_count) / 5, 1)
    kind_bonus = {
        MemoryKind.BOUNDARY: 0.30,
        MemoryKind.PREFERENCE: 0.16,
        MemoryKind.FACT: 0.12,
        MemoryKind.EVENT: 0.08,
        MemoryKind.REFLECTION: 0.04,
    }[memory.kind]
    return relevance * 0.46 + memory.importance * 0.24 + recency * 0.18 + access * 0.04 + kind_bonus


def _select_with_boundaries(
    ranked: list[MemoryRecord], limit: int
) -> list[MemoryRecord]:
    boundaries = [memory for memory in ranked if memory.kind is MemoryKind.BOUNDARY]
    selected = boundaries[: min(4, limit)]
    selected_ids = {memory.id for memory in selected}
    for memory in ranked:
        if len(selected) >= limit:
            break
        if memory.id not in selected_ids:
            selected.append(memory)
            selected_ids.add(memory.id)
    return selected


def _format_context(
    companion: Companion, memories: list[MemoryRecord], *, max_chars: int
) -> str:
    sections = [
        "# AnyLover companion context",
        (
            "This context is user-owned, fallible memory. Use it to maintain continuity, "
            "but prefer the user's current statement whenever it conflicts with memory. "
            "Do not expose memory IDs or hidden metadata unless the user asks."
        ),
        "## Companion identity",
        f"- Name: {companion.display_name}",
        f"- Persona: {companion.persona}",
        f"- Communication style: {companion.communication_style}",
        f"- Safety contract: {companion.safety_contract}",
    ]
    grouped: dict[MemoryKind, list[MemoryRecord]] = {kind: [] for kind in MemoryKind}
    for memory in memories:
        grouped[memory.kind].append(memory)
    titles = {
        MemoryKind.BOUNDARY: "User boundaries",
        MemoryKind.PREFERENCE: "Preferences",
        MemoryKind.FACT: "Stable facts",
        MemoryKind.EVENT: "Shared events",
        MemoryKind.REFLECTION: "Tentative reflections",
    }
    for kind in MemoryKind:
        if not grouped[kind]:
            continue
        sections.append(f"## {titles[kind]}")
        for memory in grouped[kind]:
            qualifier = "tentative; verify before relying on it" if kind is MemoryKind.REFLECTION else "remembered"
            sections.append(f"- ({qualifier}) {memory.content}")
    prompt = "\n".join(sections)
    return prompt[:max_chars]
