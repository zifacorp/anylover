"""Command-line interface for users and generic agent shells."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Sequence

from anylover.api_server import build_server
from anylover.backup import (
    BackupError,
    create_encrypted_backup,
    download_encrypted_backup,
    restore_encrypted_backup,
    upload_encrypted_backup,
)
from anylover.config import Settings
from anylover.service import AnyLoverService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="anylover", description="Local-first companion memory runtime"
    )
    parser.add_argument("--db", type=Path, help="Override the SQLite database path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create or update the companion")
    init_parser.add_argument("--name", default="Any")
    init_parser.add_argument("--companion-id")
    init_parser.add_argument("--persona")
    init_parser.add_argument("--style")
    init_parser.add_argument("--safety-contract")

    subparsers.add_parser("companion", help="Show the configured companion")

    remember_parser = subparsers.add_parser("remember", help="Store one durable memory")
    remember_parser.add_argument("content")
    remember_parser.add_argument(
        "--kind",
        choices=["fact", "preference", "boundary", "event", "reflection"],
        default="fact",
    )
    remember_parser.add_argument("--importance", type=float, default=0.5)
    remember_parser.add_argument(
        "--sensitivity", choices=["normal", "sensitive", "secret"], default="normal"
    )
    remember_parser.add_argument(
        "--consent", choices=["explicit", "routine", "inferred"], default="explicit"
    )
    remember_parser.add_argument("--surface", default="cli")
    remember_parser.add_argument("--session-id")
    remember_parser.add_argument("--supersedes")

    context_parser = subparsers.add_parser("context", help="Build prompt-ready context")
    context_parser.add_argument("--query", default="")
    context_parser.add_argument("--limit", type=int, default=12)
    context_parser.add_argument("--max-chars", type=int, default=6000)
    context_parser.add_argument("--json", action="store_true")

    list_parser = subparsers.add_parser("list", help="Inspect stored memories")
    list_parser.add_argument("--limit", type=int, default=100)
    list_parser.add_argument("--json", action="store_true")

    forget_parser = subparsers.add_parser("forget", help="Delete one memory")
    forget_parser.add_argument("memory_id")
    forget_parser.add_argument("--confirm", required=True, choices=["DELETE"])

    session_parser = subparsers.add_parser("session", help="Create a session record")
    session_parser.add_argument("--surface", required=True)
    session_parser.add_argument("--external-id")

    serve_parser = subparsers.add_parser("serve", help="Serve the mobile/gateway HTTP API")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8765)
    serve_parser.add_argument("--token-env", default="ANYLOVER_API_TOKEN")

    subparsers.add_parser("mcp", help="Run the MCP stdio server")

    backup_parser = subparsers.add_parser("backup", help="Encrypted backup operations")
    backup_subparsers = backup_parser.add_subparsers(dest="backup_command", required=True)
    backup_create = backup_subparsers.add_parser("create")
    backup_create.add_argument("output", type=Path)
    backup_create.add_argument("--passphrase-env", default="ANYLOVER_BACKUP_PASSPHRASE")
    backup_restore = backup_subparsers.add_parser("restore")
    backup_restore.add_argument("bundle", type=Path)
    backup_restore.add_argument("output", type=Path)
    backup_restore.add_argument("--overwrite", action="store_true")
    backup_restore.add_argument("--passphrase-env", default="ANYLOVER_BACKUP_PASSPHRASE")
    backup_upload = backup_subparsers.add_parser("upload")
    backup_upload.add_argument("bundle", type=Path)
    backup_upload.add_argument("url")
    backup_upload.add_argument("--bearer-token-env")
    backup_upload.add_argument("--username-env")
    backup_upload.add_argument("--password-env")
    backup_download = backup_subparsers.add_parser("download")
    backup_download.add_argument("url")
    backup_download.add_argument("output", type=Path)
    backup_download.add_argument("--bearer-token-env")
    backup_download.add_argument("--username-env")
    backup_download.add_argument("--password-env")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "mcp":
        from anylover.mcp_server import main as mcp_main

        return mcp_main()

    settings = Settings.from_env(db_path=args.db)
    service = AnyLoverService(settings)
    service.ensure_default_companion()
    try:
        if args.command == "init":
            try:
                current = service.get_companion(args.companion_id)
            except KeyError:
                current = service.get_companion()
            companion = service.configure_companion(
                companion_id=args.companion_id,
                display_name=args.name,
                persona=args.persona or current.persona,
                communication_style=args.style or current.communication_style,
                safety_contract=args.safety_contract or current.safety_contract,
            )
            _print_json(companion.to_dict())
            return 0
        if args.command == "companion":
            _print_json(service.get_companion().to_dict())
            return 0
        if args.command == "remember":
            memory, deduplicated = service.remember(
                content=args.content,
                kind=args.kind,
                importance=args.importance,
                sensitivity=args.sensitivity,
                consent_basis=args.consent,
                source_surface=args.surface,
                source_session_id=args.session_id,
                supersedes_id=args.supersedes,
            )
            _print_json({"memory": memory.to_dict(), "deduplicated": deduplicated})
            return 0
        if args.command == "context":
            bundle = service.build_context(
                query=args.query, limit=args.limit, max_chars=args.max_chars
            )
            if args.json:
                _print_json(bundle.to_dict())
            else:
                print(bundle.prompt)
            return 0
        if args.command == "list":
            memories = service.list_memories(limit=args.limit)
            if args.json:
                _print_json({"memories": [memory.to_dict() for memory in memories]})
            else:
                for memory in memories:
                    print(f"{memory.id}\t{memory.kind.value}\t{memory.content}")
            return 0
        if args.command == "forget":
            deleted = service.forget(
                args.memory_id,
                confirmation=args.confirm,
                actor="cli",
            )
            _print_json({"deleted": deleted, "memory_id": args.memory_id})
            return 0
        if args.command == "session":
            _print_json(
                {
                    "session_id": service.start_session(
                        surface=args.surface, external_session_id=args.external_id
                    )
                }
            )
            return 0
        if args.command == "serve":
            token = os.environ.get(args.token_env)
            server = build_server(
                service, host=args.host, port=args.port, api_token=token
            )
            print(f"AnyLover API listening on http://{args.host}:{server.server_port}")
            server.serve_forever()
            return 0
        if args.command == "backup":
            return _run_backup(args, settings)
    except (BackupError, KeyError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 1


def _run_backup(args: argparse.Namespace, settings: Settings) -> int:
    if args.backup_command == "create":
        path = create_encrypted_backup(
            settings.db_path,
            args.output,
            passphrase=_required_env(args.passphrase_env),
        )
        print(path)
        return 0
    if args.backup_command == "restore":
        path = restore_encrypted_backup(
            args.bundle,
            args.output,
            passphrase=_required_env(args.passphrase_env),
            overwrite=args.overwrite,
        )
        print(path)
        return 0
    credential_args = {
        "bearer_token": _optional_env(args.bearer_token_env),
        "username": _optional_env(args.username_env),
        "password": _optional_env(args.password_env),
    }
    if args.backup_command == "upload":
        status = upload_encrypted_backup(args.bundle, args.url, **credential_args)
        _print_json({"status": status, "uploaded": True})
        return 0
    if args.backup_command == "download":
        path = download_encrypted_backup(args.url, args.output, **credential_args)
        print(path)
        return 0
    return 1


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"required environment variable is not set: {name}")
    return value


def _optional_env(name: str | None) -> str | None:
    return os.environ.get(name) if name else None


def _print_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
