"""Small authenticated JSON API for mobile clients and remote gateways."""

from __future__ import annotations

import hmac
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from anylover.service import AnyLoverService


MAX_REQUEST_BYTES = 1_000_000


class AnyLoverHTTPServer(ThreadingHTTPServer):
    service: AnyLoverService
    api_token: str | None


def build_server(
    service: AnyLoverService,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    api_token: str | None = None,
) -> AnyLoverHTTPServer:
    loopback = host in {"127.0.0.1", "localhost", "::1"}
    if not loopback and not api_token:
        raise ValueError("ANYLOVER_API_TOKEN is required when binding beyond loopback")
    server = AnyLoverHTTPServer((host, port), AnyLoverRequestHandler)
    server.service = service
    server.api_token = api_token
    return server


class AnyLoverRequestHandler(BaseHTTPRequestHandler):
    server: AnyLoverHTTPServer
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._json(HTTPStatus.OK, {"status": "ok"})
            return
        if not self._authorized():
            return
        query = parse_qs(parsed.query)
        try:
            if parsed.path == "/v1/companion":
                companion = self.server.service.get_companion(
                    _first(query, "companion_id")
                )
                self._json(HTTPStatus.OK, companion.to_dict())
                return
            if parsed.path == "/v1/context":
                context = self.server.service.build_context(
                    query=_first(query, "query") or "",
                    limit=_int_query(query, "limit", 12),
                    max_chars=_int_query(query, "max_chars", 6000),
                    user_id=_first(query, "user_id"),
                    companion_id=_first(query, "companion_id"),
                )
                self._json(HTTPStatus.OK, context.to_dict())
                return
            if parsed.path == "/v1/memories":
                memories = self.server.service.list_memories(
                    limit=_int_query(query, "limit", 100),
                    user_id=_first(query, "user_id"),
                    companion_id=_first(query, "companion_id"),
                )
                self._json(
                    HTTPStatus.OK,
                    {"memories": [memory.to_dict() for memory in memories]},
                )
                return
            self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
        except (KeyError, TypeError, ValueError) as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})

    def do_POST(self) -> None:  # noqa: N802
        if not self._authorized():
            return
        parsed = urlparse(self.path)
        try:
            payload = self._read_json()
            if parsed.path == "/v1/memories":
                memory, deduplicated = self.server.service.remember(
                    content=payload["content"],
                    kind=payload.get("kind", "fact"),
                    importance=float(payload.get("importance", 0.5)),
                    sensitivity=payload.get("sensitivity", "normal"),
                    consent_basis=payload.get("consent_basis", "explicit"),
                    source_surface=payload.get("source_surface", "mobile"),
                    source_session_id=payload.get("source_session_id"),
                    user_id=payload.get("user_id"),
                    companion_id=payload.get("companion_id"),
                    supersedes_id=payload.get("supersedes_id"),
                    metadata=payload.get("metadata"),
                )
                self._json(
                    HTTPStatus.CREATED,
                    {"memory": memory.to_dict(), "deduplicated": deduplicated},
                )
                return
            if parsed.path == "/v1/sessions":
                session_id = self.server.service.start_session(
                    surface=payload.get("surface", "mobile"),
                    external_session_id=payload.get("external_session_id"),
                    user_id=payload.get("user_id"),
                    companion_id=payload.get("companion_id"),
                    metadata=payload.get("metadata"),
                )
                self._json(HTTPStatus.CREATED, {"session_id": session_id})
                return
            if parsed.path == "/v1/companion":
                companion = self.server.service.configure_companion(
                    companion_id=payload.get("companion_id"),
                    display_name=payload["display_name"],
                    persona=payload.get("persona") or self.server.service.get_companion().persona,
                    communication_style=payload.get("communication_style")
                    or self.server.service.get_companion().communication_style,
                    safety_contract=payload.get("safety_contract")
                    or self.server.service.get_companion().safety_contract,
                )
                self._json(HTTPStatus.OK, companion.to_dict())
                return
            self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
        except (KeyError, TypeError, ValueError) as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})

    def do_DELETE(self) -> None:  # noqa: N802
        if not self._authorized():
            return
        parsed = urlparse(self.path)
        prefix = "/v1/memories/"
        if not parsed.path.startswith(prefix):
            self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        memory_id = parsed.path[len(prefix) :]
        query = parse_qs(parsed.query)
        try:
            deleted = self.server.service.forget(
                memory_id,
                confirmation=self.headers.get("X-AnyLover-Confirm", ""),
                actor="http-api",
                user_id=_first(query, "user_id"),
                companion_id=_first(query, "companion_id"),
            )
            self._json(HTTPStatus.OK, {"deleted": deleted, "memory_id": memory_id})
        except (KeyError, TypeError, ValueError) as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})

    def log_message(self, format: str, *args: Any) -> None:
        # Intentionally avoid logging paths, query strings, or authorization data.
        return

    def _authorized(self) -> bool:
        expected = self.server.api_token
        if expected is None:
            return True
        supplied = self.headers.get("Authorization", "")
        valid = supplied.startswith("Bearer ") and hmac.compare_digest(
            supplied[7:], expected
        )
        if not valid:
            self._json(
                HTTPStatus.UNAUTHORIZED,
                {"error": "unauthorized"},
                extra_headers={"WWW-Authenticate": "Bearer"},
            )
        return valid

    def _read_json(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
            raise ValueError("invalid request size")
        try:
            payload = json.loads(self.rfile.read(content_length))
        except json.JSONDecodeError as exc:
            raise ValueError("invalid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    def _json(
        self,
        status: HTTPStatus,
        payload: dict[str, Any],
        *,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)


def _first(query: dict[str, list[str]], key: str) -> str | None:
    values = query.get(key)
    return values[0] if values else None


def _int_query(query: dict[str, list[str]], key: str, default: int) -> int:
    value = _first(query, key)
    return int(value) if value is not None else default

