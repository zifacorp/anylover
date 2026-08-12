#!/usr/bin/env python3
"""Safely merge one STDIO server into an MCP JSON configuration file."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ConfigConflict(RuntimeError):
    """Raised when an existing named MCP server would be overwritten."""


def merge_mcp_config(
    path: Path,
    *,
    name: str,
    command: str,
    replace: bool = False,
) -> str:
    desired = {"type": "stdio", "command": command, "args": []}
    existed = path.exists()
    if existed:
        try:
            root: Any = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    else:
        root = {}
    if not isinstance(root, dict):
        raise ValueError(f"MCP configuration root must be an object: {path}")
    servers = root.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise ValueError(f"mcpServers must be an object: {path}")

    existing = servers.get(name)
    if existing == desired:
        return "unchanged"
    if existing is not None and not replace:
        raise ConfigConflict(f"MCP server already exists with different settings: {name}")

    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if existed:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        backup = path.with_name(f"{path.name}.backup-{timestamp}-{uuid.uuid4().hex[:8]}")
        shutil.copy2(path, backup)

    servers[name] = desired
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(root, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        temp_path.chmod(0o600)
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)
    return "updated" if existing is not None else "created"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--command", required=True)
    parser.add_argument("--replace", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = merge_mcp_config(
            args.file,
            name=args.name,
            command=args.command,
            replace=args.replace,
        )
    except (ConfigConflict, OSError, ValueError) as exc:
        print(str(exc), file=os.sys.stderr)
        return 2
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
