"""SQLite persistence. The database is local and user-owned."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator

from anylover.models import (
    Companion,
    ConsentBasis,
    MemoryKind,
    MemoryRecord,
    Sensitivity,
)


SCHEMA_VERSION = 1


def utcnow() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class Database:
    def __init__(self, path: Path):
        self.path = path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS schema_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS companions (
                    id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    persona TEXT NOT NULL,
                    communication_style TEXT NOT NULL,
                    safety_contract TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    companion_id TEXT NOT NULL REFERENCES companions(id),
                    user_id TEXT NOT NULL,
                    surface TEXT NOT NULL,
                    external_session_id TEXT,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    companion_id TEXT NOT NULL REFERENCES companions(id),
                    user_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    content TEXT NOT NULL,
                    normalized_content TEXT NOT NULL,
                    importance REAL NOT NULL CHECK(importance >= 0 AND importance <= 1),
                    sensitivity TEXT NOT NULL,
                    consent_basis TEXT NOT NULL,
                    source_surface TEXT NOT NULL,
                    source_session_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_accessed_at TEXT,
                    access_count INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'active',
                    supersedes_id TEXT REFERENCES memories(id),
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                );

                CREATE INDEX IF NOT EXISTS memories_scope_idx
                ON memories(companion_id, user_id, status, kind, updated_at DESC);

                CREATE UNIQUE INDEX IF NOT EXISTS memories_active_dedupe_idx
                ON memories(companion_id, user_id, kind, normalized_content)
                WHERE status = 'active';

                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    action TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    target_id TEXT,
                    created_at TEXT NOT NULL,
                    detail_json TEXT NOT NULL DEFAULT '{}'
                );
                """
            )
            connection.execute(
                "INSERT INTO schema_meta(key, value) VALUES('schema_version', ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (str(SCHEMA_VERSION),),
            )
        try:
            self.path.chmod(0o600)
        except OSError:
            pass

    def upsert_companion(
        self,
        *,
        companion_id: str,
        display_name: str,
        persona: str,
        communication_style: str,
        safety_contract: str,
    ) -> Companion:
        now = utcnow()
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO companions(
                    id, display_name, persona, communication_style,
                    safety_contract, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    display_name = excluded.display_name,
                    persona = excluded.persona,
                    communication_style = excluded.communication_style,
                    safety_contract = excluded.safety_contract,
                    updated_at = excluded.updated_at
                """,
                (
                    companion_id,
                    display_name,
                    persona,
                    communication_style,
                    safety_contract,
                    now,
                    now,
                ),
            )
            row = connection.execute(
                "SELECT * FROM companions WHERE id = ?", (companion_id,)
            ).fetchone()
            self._audit(
                connection,
                action="companion.upsert",
                actor="user",
                target_type="companion",
                target_id=companion_id,
            )
        return _companion_from_row(row)

    def get_companion(self, companion_id: str) -> Companion | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM companions WHERE id = ?", (companion_id,)
            ).fetchone()
        return _companion_from_row(row) if row else None

    def start_session(
        self,
        *,
        companion_id: str,
        user_id: str,
        surface: str,
        external_session_id: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        session_id = str(uuid.uuid4())
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO sessions(
                    id, companion_id, user_id, surface, external_session_id,
                    started_at, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    companion_id,
                    user_id,
                    surface,
                    external_session_id,
                    utcnow(),
                    json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True),
                ),
            )
            self._audit(
                connection,
                action="session.start",
                actor=surface,
                target_type="session",
                target_id=session_id,
            )
        return session_id

    def create_memory(
        self,
        *,
        companion_id: str,
        user_id: str,
        kind: MemoryKind,
        content: str,
        normalized_content: str,
        importance: float,
        sensitivity: Sensitivity,
        consent_basis: ConsentBasis,
        source_surface: str,
        source_session_id: str | None,
        supersedes_id: str | None,
        metadata: dict[str, Any] | None,
    ) -> tuple[MemoryRecord, bool]:
        memory_id = str(uuid.uuid4())
        now = utcnow()
        with self.connect() as connection:
            existing = connection.execute(
                """
                SELECT * FROM memories
                WHERE companion_id = ? AND user_id = ? AND kind = ?
                  AND normalized_content = ? AND status = 'active'
                """,
                (companion_id, user_id, kind.value, normalized_content),
            ).fetchone()
            if existing:
                connection.execute(
                    """
                    UPDATE memories
                    SET importance = MAX(importance, ?), updated_at = ?,
                        source_surface = ?, source_session_id = COALESCE(?, source_session_id)
                    WHERE id = ?
                    """,
                    (importance, now, source_surface, source_session_id, existing["id"]),
                )
                row = connection.execute(
                    "SELECT * FROM memories WHERE id = ?", (existing["id"],)
                ).fetchone()
                self._audit(
                    connection,
                    action="memory.deduplicate",
                    actor=source_surface,
                    target_type="memory",
                    target_id=existing["id"],
                )
                return _memory_from_row(row), True

            if supersedes_id:
                connection.execute(
                    "UPDATE memories SET status = 'superseded', updated_at = ? "
                    "WHERE id = ? AND companion_id = ? AND user_id = ?",
                    (now, supersedes_id, companion_id, user_id),
                )
            connection.execute(
                """
                INSERT INTO memories(
                    id, companion_id, user_id, kind, content, normalized_content,
                    importance, sensitivity, consent_basis, source_surface,
                    source_session_id, created_at, updated_at, supersedes_id,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory_id,
                    companion_id,
                    user_id,
                    kind.value,
                    content,
                    normalized_content,
                    importance,
                    sensitivity.value,
                    consent_basis.value,
                    source_surface,
                    source_session_id,
                    now,
                    now,
                    supersedes_id,
                    json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True),
                ),
            )
            row = connection.execute(
                "SELECT * FROM memories WHERE id = ?", (memory_id,)
            ).fetchone()
            self._audit(
                connection,
                action="memory.create",
                actor=source_surface,
                target_type="memory",
                target_id=memory_id,
                detail={"kind": kind.value, "consent_basis": consent_basis.value},
            )
        return _memory_from_row(row), False

    def list_memories(
        self,
        *,
        companion_id: str,
        user_id: str,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[MemoryRecord]:
        status_clause = "" if include_deleted else "AND status = 'active'"
        with self.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT * FROM memories
                WHERE companion_id = ? AND user_id = ? {status_clause}
                ORDER BY updated_at DESC LIMIT ?
                """,
                (companion_id, user_id, limit),
            ).fetchall()
        return [_memory_from_row(row) for row in rows]

    def forget_memory(
        self,
        *,
        memory_id: str,
        companion_id: str,
        user_id: str,
        actor: str,
    ) -> bool:
        now = utcnow()
        with self.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE memories
                SET status = 'deleted', content = '[deleted by user]',
                    normalized_content = ?, metadata_json = '{}', updated_at = ?
                WHERE id = ? AND companion_id = ? AND user_id = ?
                  AND status != 'deleted'
                """,
                (f"deleted:{memory_id}", now, memory_id, companion_id, user_id),
            )
            changed = cursor.rowcount > 0
            if changed:
                self._audit(
                    connection,
                    action="memory.delete",
                    actor=actor,
                    target_type="memory",
                    target_id=memory_id,
                )
        return changed

    def mark_accessed(self, memory_ids: list[str]) -> None:
        if not memory_ids:
            return
        placeholders = ",".join("?" for _ in memory_ids)
        with self.connect() as connection:
            connection.execute(
                f"""
                UPDATE memories
                SET last_accessed_at = ?, access_count = access_count + 1
                WHERE id IN ({placeholders})
                """,
                (utcnow(), *memory_ids),
            )

    @staticmethod
    def _audit(
        connection: sqlite3.Connection,
        *,
        action: str,
        actor: str,
        target_type: str,
        target_id: str | None,
        detail: dict[str, Any] | None = None,
    ) -> None:
        connection.execute(
            """
            INSERT INTO audit_events(
                id, action, actor, target_type, target_id, created_at, detail_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                action,
                actor,
                target_type,
                target_id,
                utcnow(),
                json.dumps(detail or {}, ensure_ascii=False, sort_keys=True),
            ),
        )


def _companion_from_row(row: sqlite3.Row) -> Companion:
    return Companion(
        id=row["id"],
        display_name=row["display_name"],
        persona=row["persona"],
        communication_style=row["communication_style"],
        safety_contract=row["safety_contract"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _memory_from_row(row: sqlite3.Row) -> MemoryRecord:
    return MemoryRecord(
        id=row["id"],
        companion_id=row["companion_id"],
        user_id=row["user_id"],
        kind=MemoryKind(row["kind"]),
        content=row["content"],
        importance=float(row["importance"]),
        sensitivity=Sensitivity(row["sensitivity"]),
        consent_basis=ConsentBasis(row["consent_basis"]),
        source_surface=row["source_surface"],
        source_session_id=row["source_session_id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        last_accessed_at=row["last_accessed_at"],
        access_count=int(row["access_count"]),
        status=row["status"],
        supersedes_id=row["supersedes_id"],
        metadata=json.loads(row["metadata_json"] or "{}"),
    )
