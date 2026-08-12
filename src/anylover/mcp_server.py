"""Minimal MCP stdio server exposing the companion memory runtime."""

from __future__ import annotations

import json
import sys
from typing import Any

from anylover import __version__
from anylover.config import Settings
from anylover.service import AnyLoverService


SERVER_INSTRUCTIONS = (
    "AnyLover is user-owned companion memory. Read context near the start of a "
    "companion interaction. Store only durable, useful information with an honest "
    "consent_basis. Never store passwords, API keys, private keys, or authentication tokens. "
    "Do not claim memory is infallible; the user's current correction wins."
)


TOOLS: list[dict[str, Any]] = [
    {
        "name": "anylover_get_context",
        "description": "Read prompt-ready companion identity and relevant user-owned memories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Current topic or user message."},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 12},
                "max_chars": {"type": "integer", "minimum": 500, "maximum": 20000, "default": 6000},
                "user_id": {"type": "string"},
                "companion_id": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "idempotentHint": True},
    },
    {
        "name": "anylover_remember",
        "description": "Persist one durable fact, preference, boundary, event, or tentative reflection.",
        "inputSchema": {
            "type": "object",
            "required": ["content", "kind", "consent_basis", "source_surface"],
            "properties": {
                "content": {"type": "string", "minLength": 2, "maxLength": 4000},
                "kind": {"enum": ["fact", "preference", "boundary", "event", "reflection"]},
                "importance": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.5},
                "sensitivity": {"enum": ["normal", "sensitive", "secret"], "default": "normal"},
                "consent_basis": {"enum": ["explicit", "routine", "inferred"]},
                "source_surface": {"type": "string", "description": "codex, chatgpt, claude-code, workbuddy, mobile, etc."},
                "source_session_id": {"type": "string"},
                "supersedes_id": {"type": "string"},
                "user_id": {"type": "string"},
                "companion_id": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "idempotentHint": True},
    },
    {
        "name": "anylover_list_memories",
        "description": "List stored memory records so the user can inspect or correct them.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "minimum": 1, "maximum": 500, "default": 100},
                "user_id": {"type": "string"},
                "companion_id": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "idempotentHint": True},
    },
    {
        "name": "anylover_forget",
        "description": "Delete the content of one memory and retain only a tombstone for sync/audit.",
        "inputSchema": {
            "type": "object",
            "required": ["memory_id", "confirmation", "actor"],
            "properties": {
                "memory_id": {"type": "string"},
                "confirmation": {"type": "string", "const": "DELETE"},
                "actor": {"type": "string"},
                "user_id": {"type": "string"},
                "companion_id": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True},
    },
    {
        "name": "anylover_start_session",
        "description": "Create a cross-surface session provenance record without storing chat text.",
        "inputSchema": {
            "type": "object",
            "required": ["surface"],
            "properties": {
                "surface": {"type": "string"},
                "external_session_id": {"type": "string"},
                "user_id": {"type": "string"},
                "companion_id": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "idempotentHint": False},
    },
]


def dispatch(message: dict[str, Any], service: AnyLoverService) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    if request_id is None:
        return None
    try:
        if method == "initialize":
            requested = message.get("params", {}).get("protocolVersion", "2025-03-26")
            return _result(
                request_id,
                {
                    "protocolVersion": requested,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "anylover", "version": __version__},
                    "instructions": SERVER_INSTRUCTIONS,
                },
            )
        if method == "ping":
            return _result(request_id, {})
        if method == "tools/list":
            return _result(request_id, {"tools": TOOLS})
        if method == "tools/call":
            params = message.get("params") or {}
            tool_name = params.get("name")
            arguments = params.get("arguments") or {}
            payload = _call_tool(tool_name, arguments, service)
            return _result(
                request_id,
                {
                    "content": [
                        {"type": "text", "text": json.dumps(payload, ensure_ascii=False)}
                    ],
                    "structuredContent": payload,
                    "isError": False,
                },
            )
        return _error(request_id, -32601, f"Method not found: {method}")
    except (KeyError, TypeError, ValueError) as exc:
        return _result(
            request_id,
            {
                "content": [{"type": "text", "text": str(exc)}],
                "isError": True,
            },
        )
    except Exception as exc:
        print(f"anylover MCP internal error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return _error(request_id, -32603, "Internal error")


def _call_tool(
    name: str | None, arguments: dict[str, Any], service: AnyLoverService
) -> dict[str, Any]:
    if name == "anylover_get_context":
        return service.build_context(
            query=arguments.get("query", ""),
            limit=int(arguments.get("limit", 12)),
            max_chars=int(arguments.get("max_chars", 6000)),
            user_id=arguments.get("user_id"),
            companion_id=arguments.get("companion_id"),
        ).to_dict()
    if name == "anylover_remember":
        memory, deduplicated = service.remember(
            content=arguments["content"],
            kind=arguments["kind"],
            importance=float(arguments.get("importance", 0.5)),
            sensitivity=arguments.get("sensitivity", "normal"),
            consent_basis=arguments["consent_basis"],
            source_surface=arguments["source_surface"],
            source_session_id=arguments.get("source_session_id"),
            user_id=arguments.get("user_id"),
            companion_id=arguments.get("companion_id"),
            supersedes_id=arguments.get("supersedes_id"),
        )
        return {"memory": memory.to_dict(), "deduplicated": deduplicated}
    if name == "anylover_list_memories":
        memories = service.list_memories(
            limit=int(arguments.get("limit", 100)),
            user_id=arguments.get("user_id"),
            companion_id=arguments.get("companion_id"),
        )
        return {"memories": [memory.to_dict() for memory in memories]}
    if name == "anylover_forget":
        deleted = service.forget(
            arguments["memory_id"],
            confirmation=arguments["confirmation"],
            actor=arguments["actor"],
            user_id=arguments.get("user_id"),
            companion_id=arguments.get("companion_id"),
        )
        return {"deleted": deleted, "memory_id": arguments["memory_id"]}
    if name == "anylover_start_session":
        return {
            "session_id": service.start_session(
                surface=arguments["surface"],
                external_session_id=arguments.get("external_session_id"),
                user_id=arguments.get("user_id"),
                companion_id=arguments.get("companion_id"),
            )
        }
    raise ValueError(f"Unknown tool: {name}")


def _result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def main() -> int:
    service = AnyLoverService(Settings.from_env())
    service.ensure_default_companion()
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            response = _error(None, -32700, "Parse error")
        else:
            response = dispatch(message, service)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
