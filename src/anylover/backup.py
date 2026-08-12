"""Encrypted local backup bundles and provider-neutral HTTPS transfer."""

from __future__ import annotations

import base64
import json
import os
import sqlite3
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path


MAGIC = b"ANYLOVER-BACKUP\x00\x01\n"


class BackupError(RuntimeError):
    pass


def create_encrypted_backup(
    database_path: Path, output_path: Path, *, passphrase: str
) -> Path:
    """Create an AES-256-GCM bundle from a consistent SQLite snapshot."""
    _validate_passphrase(passphrase)
    if not database_path.exists():
        raise BackupError(f"database does not exist: {database_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    snapshot_fd, snapshot_name = tempfile.mkstemp(prefix="anylover-snapshot-", suffix=".sqlite3")
    os.close(snapshot_fd)
    snapshot_path = Path(snapshot_name)
    temp_output = output_path.with_name(f".{output_path.name}.{os.getpid()}.tmp")
    try:
        source = sqlite3.connect(database_path)
        target = sqlite3.connect(snapshot_path)
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()
        payload = snapshot_path.read_bytes()
        salt = os.urandom(16)
        nonce = os.urandom(12)
        header = {
            "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "cipher": "AES-256-GCM",
            "kdf": "scrypt",
            "n": 32768,
            "r": 8,
            "p": 1,
            "salt": base64.b64encode(salt).decode("ascii"),
            "nonce": base64.b64encode(nonce).decode("ascii"),
            "schema": 1,
        }
        header_bytes = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
        aad = MAGIC + header_bytes + b"\n"
        ciphertext = _aesgcm(_derive_key(passphrase, salt, header)).encrypt(
            nonce, payload, aad
        )
        with temp_output.open("wb") as handle:
            handle.write(aad)
            handle.write(ciphertext)
            handle.flush()
            os.fsync(handle.fileno())
        temp_output.chmod(0o600)
        os.replace(temp_output, output_path)
        return output_path
    finally:
        snapshot_path.unlink(missing_ok=True)
        temp_output.unlink(missing_ok=True)


def restore_encrypted_backup(
    bundle_path: Path,
    output_database_path: Path,
    *,
    passphrase: str,
    overwrite: bool = False,
) -> Path:
    """Decrypt into a separate SQLite file and verify integrity."""
    _validate_passphrase(passphrase)
    if output_database_path.exists() and not overwrite:
        raise BackupError(f"output already exists: {output_database_path}")
    header, header_bytes, ciphertext = _read_bundle(bundle_path)
    try:
        salt = base64.b64decode(header["salt"], validate=True)
        nonce = base64.b64decode(header["nonce"], validate=True)
    except (KeyError, ValueError) as exc:
        raise BackupError("invalid backup header") from exc
    aad = MAGIC + header_bytes + b"\n"
    try:
        plaintext = _aesgcm(_derive_key(passphrase, salt, header)).decrypt(
            nonce, ciphertext, aad
        )
    except Exception as exc:
        raise BackupError("backup authentication failed; passphrase or file is invalid") from exc
    if not plaintext.startswith(b"SQLite format 3\x00"):
        raise BackupError("decrypted payload is not a SQLite database")

    output_database_path.parent.mkdir(parents=True, exist_ok=True)
    temp_output = output_database_path.with_name(
        f".{output_database_path.name}.{os.getpid()}.tmp"
    )
    try:
        temp_output.write_bytes(plaintext)
        connection = sqlite3.connect(temp_output)
        try:
            verdict = connection.execute("PRAGMA integrity_check").fetchone()[0]
        finally:
            connection.close()
        if verdict != "ok":
            raise BackupError(f"restored database failed integrity check: {verdict}")
        temp_output.chmod(0o600)
        os.replace(temp_output, output_database_path)
        return output_database_path
    finally:
        temp_output.unlink(missing_ok=True)


def upload_encrypted_backup(
    bundle_path: Path,
    url: str,
    *,
    bearer_token: str | None = None,
    username: str | None = None,
    password: str | None = None,
    timeout: float = 60,
) -> int:
    """PUT an already-encrypted bundle to HTTPS/WebDAV/presigned object storage."""
    _validate_remote_url(url)
    headers = {"Content-Type": "application/octet-stream"}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    elif username is not None and password is not None:
        credential = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers["Authorization"] = f"Basic {credential}"
    request = urllib.request.Request(
        url,
        data=bundle_path.read_bytes(),
        headers=headers,
        method="PUT",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status)
    except urllib.error.URLError as exc:
        raise BackupError(f"backup upload failed: {exc.reason}") from exc


def download_encrypted_backup(
    url: str,
    output_path: Path,
    *,
    bearer_token: str | None = None,
    username: str | None = None,
    password: str | None = None,
    timeout: float = 60,
) -> Path:
    """GET an encrypted bundle without decrypting it."""
    _validate_remote_url(url)
    headers: dict[str, str] = {}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    elif username is not None and password is not None:
        credential = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers["Authorization"] = f"Basic {credential}"
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
    except urllib.error.URLError as exc:
        raise BackupError(f"backup download failed: {exc.reason}") from exc
    if not payload.startswith(MAGIC):
        raise BackupError("downloaded object is not an AnyLover backup")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(payload)
    output_path.chmod(0o600)
    return output_path


def _read_bundle(bundle_path: Path) -> tuple[dict[str, object], bytes, bytes]:
    payload = bundle_path.read_bytes()
    if not payload.startswith(MAGIC):
        raise BackupError("not an AnyLover backup")
    header_start = len(MAGIC)
    header_end = payload.find(b"\n", header_start)
    if header_end == -1:
        raise BackupError("backup header is truncated")
    header_bytes = payload[header_start:header_end]
    try:
        header = json.loads(header_bytes)
    except json.JSONDecodeError as exc:
        raise BackupError("backup header is invalid JSON") from exc
    return header, header_bytes, payload[header_end + 1 :]


def _derive_key(passphrase: str, salt: bytes, header: dict[str, object]) -> bytes:
    try:
        from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    except ImportError as exc:
        raise BackupError("install the 'cryptography' package to use encrypted backups") from exc
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=int(header["n"]),
        r=int(header["r"]),
        p=int(header["p"]),
    )
    return kdf.derive(passphrase.encode("utf-8"))


def _aesgcm(key: bytes):
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as exc:
        raise BackupError("install the 'cryptography' package to use encrypted backups") from exc
    return AESGCM(key)


def _validate_passphrase(passphrase: str) -> None:
    if len(passphrase) < 12:
        raise BackupError("backup passphrase must contain at least 12 characters")


def _validate_remote_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    loopback = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
    if parsed.scheme != "https" and not (parsed.scheme == "http" and loopback):
        raise BackupError("backup transfer requires HTTPS (HTTP is allowed only on loopback)")

