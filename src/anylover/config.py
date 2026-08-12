"""Runtime configuration with local-first defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    data_dir: Path
    db_path: Path
    default_user_id: str = "local-user"
    default_companion_id: str = "default"
    allow_sensitive_memory: bool = False

    @classmethod
    def from_env(cls, *, db_path: str | Path | None = None) -> "Settings":
        configured_dir = os.environ.get("ANYLOVER_HOME")
        data_dir = (
            Path(configured_dir).expanduser()
            if configured_dir
            else Path.home() / ".anylover"
        )
        configured_db = db_path or os.environ.get("ANYLOVER_DB")
        resolved_db = (
            Path(configured_db).expanduser()
            if configured_db
            else data_dir / "anylover.sqlite3"
        )
        allow_sensitive = os.environ.get("ANYLOVER_ALLOW_SENSITIVE_MEMORY", "0") in {
            "1",
            "true",
            "TRUE",
        }
        return cls(
            data_dir=data_dir,
            db_path=resolved_db,
            default_user_id=os.environ.get("ANYLOVER_USER_ID", "local-user"),
            default_companion_id=os.environ.get("ANYLOVER_COMPANION_ID", "default"),
            allow_sensitive_memory=allow_sensitive,
        )

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.db_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        try:
            self.data_dir.chmod(0o700)
        except OSError:
            pass

