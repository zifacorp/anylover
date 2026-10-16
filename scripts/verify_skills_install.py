#!/usr/bin/env python3
"""Networked Skills CLI smoke test. All installs use temporary user/config roots."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = (
    "codex", "claude-code", "cursor", "windsurf", "opencode", "gemini-cli",
    "github-copilot", "openclaw", "codebuddy",
)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="anylover-skills-") as directory:
        sandbox = Path(directory)
        env = {
            **os.environ,
            "HOME": str(sandbox),
            "XDG_CONFIG_HOME": str(sandbox / ".config"),
            "XDG_DATA_HOME": str(sandbox / ".local/share"),
            "XDG_STATE_HOME": str(sandbox / ".local/state"),
            "CODEX_HOME": str(sandbox / ".codex"),
            "CLAUDE_CONFIG_DIR": str(sandbox / ".claude"),
            "OPENCLAW_STATE_DIR": str(sandbox / ".openclaw"),
            "ANYLOVER_INSTALL_ROOT": str(sandbox / "runtime"),
            "ANYLOVER_HOME": str(sandbox / "memory"),
            "ANYLOVER_DB": str(sandbox / "memory/anylover.sqlite3"),
            "ANYLOVER_USER_ID": "portable-smoke",
            "ANYLOVER_COMPANION_ID": "default",
            "ANYLOVER_BIN_DIR": str(sandbox / "bin"),
            "ANYLOVER_WORKBUDDY_HOME": str(sandbox / ".workbuddy"),
            "ANYLOVER_PYTHON": sys.executable,
            "DISABLE_TELEMETRY": "1",
        }

        def run(*args: str, timeout: int = 180) -> str:
            result = subprocess.run(
                args, env=env, cwd=sandbox, text=True, capture_output=True,
                timeout=timeout,
            )
            if result.returncode:
                raise RuntimeError(f"{args[0]} failed:\n{result.stdout}\n{result.stderr}")
            return result.stdout

        listing = run("npx", "--yes", "skills", "add", str(ROOT), "--list")
        assert "anylover-companion" in listing, listing
        print("Repository discovery: OK", flush=True)
        installation = run(
            "npx", "--yes", "skills", "add", str(ROOT),
            "--skill", "anylover-companion", "--global", "--agent", *AGENTS,
            "--copy", "--yes",
        )
        print(installation, flush=True)
        installed = [
            # Skills CLI places universal agents (including Cursor and Codex)
            # in this shared root rather than duplicating their native folders.
            sandbox / ".agents/skills/anylover-companion",
            sandbox / ".claude/skills/anylover-companion",
            sandbox / ".codeium/windsurf/skills/anylover-companion",
            sandbox / ".openclaw/skills/anylover-companion",
            sandbox / ".codebuddy/skills/anylover-companion",
        ]
        for skill in installed:
            for relative in ("SKILL.md", "scripts/setup.sh", "references/cli.md"):
                assert (skill / relative).is_file(), f"Missing {skill / relative}"
        print(f"Skills CLI install: OK ({len(AGENTS)} agent targets)", flush=True)

        # Install from the copied Skill, outside the repository checkout.
        run("bash", str(installed[2] / "scripts/setup.sh"), "--source", str(ROOT))
        cli = str(sandbox / "runtime/venv/bin/anylover")
        profile = json.loads(run(cli, "init", "--name", "Portable Any", "--persona", "Keep me"))
        memory = json.loads(run(
            cli, "remember", "--kind", "preference", "--consent", "explicit",
            "--surface", "cursor", "--", "I prefer quiet evenings.",
        ))["memory"]
        context = json.loads(run(cli, "context", "--query", "quiet evenings", "--json"))
        assert context["memories"][0]["id"] == memory["id"]
        assert context["memories"][0]["source_surface"] == "cursor"

        # Exercise the public Bash wrapper too; existing data must survive upgrades.
        run("bash", str(ROOT / "install.sh"), "--agent", "windsurf")
        assert json.loads(run(cli, "companion")) == profile
        assert json.loads(run(cli, "list", "--json"))["memories"][0]["id"] == memory["id"]
        print("Installed-Skill bootstrap, CLI recall, and wrapper upgrade preservation: OK", flush=True)
        for config in (".codex/config.toml", ".claude.json", ".cursor/mcp.json", ".workbuddy/.mcp.json"):
            assert not (sandbox / config).exists(), f"Unexpected MCP config: {config}"
        print("No MCP config changes: OK; temporary installation cleaned up on exit.", flush=True)


if __name__ == "__main__":
    main()
