from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.merge_mcp_config import ConfigConflict, merge_mcp_config


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "integrations/anylover-companion/skills/anylover-companion"


class InstallerTest(unittest.TestCase):
    def test_companion_skill_allows_implicit_context_retrieval(self) -> None:
        skill = (
            ROOT
            / "integrations"
            / "anylover-companion"
            / "skills"
            / "anylover-companion"
        )
        instructions = (skill / "SKILL.md").read_text(encoding="utf-8")
        metadata = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("Do not require the user to name AnyLover", instructions)
        self.assertIn("call `anylover_get_context` again", instructions)
        self.assertIn("allow_implicit_invocation: true", metadata)

    def test_merge_preserves_servers_and_backs_up(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / ".mcp.json"
            config.write_text(
                json.dumps({"mcpServers": {"existing": {"command": "other"}}}),
                encoding="utf-8",
            )
            result = merge_mcp_config(
                config,
                name="anylover",
                command="/private/anylover-mcp",
            )
            self.assertEqual(result, "created")
            parsed = json.loads(config.read_text(encoding="utf-8"))
            self.assertIn("existing", parsed["mcpServers"])
            self.assertEqual(
                parsed["mcpServers"]["anylover"]["command"],
                "/private/anylover-mcp",
            )
            self.assertEqual(len(list(Path(directory).glob(".mcp.json.backup-*"))), 1)

    def test_merge_requires_explicit_replace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / ".mcp.json"
            config.write_text(
                json.dumps(
                    {
                        "mcpServers": {
                            "anylover": {
                                "type": "stdio",
                                "command": "/old/anylover-mcp",
                                "args": [],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ConfigConflict):
                merge_mcp_config(
                    config,
                    name="anylover",
                    command="/new/anylover-mcp",
                )
            result = merge_mcp_config(
                config,
                name="anylover",
                command="/new/anylover-mcp",
                replace=True,
            )
            self.assertEqual(result, "updated")

    def test_installer_dry_run_has_no_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            sandbox = Path(directory)
            runtime = sandbox / "runtime"
            completed = subprocess.run(
                [
                    "bash",
                    str(ROOT / "install.sh"),
                    "--dry-run",
                    "--agent",
                    "all",
                    "--name",
                    "Nova",
                    "--install-root",
                    str(runtime),
                ],
                cwd=ROOT,
                env={"HOME": str(sandbox), "PATH": "/usr/bin:/bin"},
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("Dry run", completed.stdout)
            self.assertIn("Nova", completed.stdout)
            self.assertIn("Codex/ChatGPT desktop", completed.stdout)
            self.assertIn("cursor (Skill + CLI)", completed.stdout)
            self.assertIn("openclaw (Skill + CLI)", completed.stdout)
            self.assertIn("npx --yes skills add", completed.stdout)
            self.assertFalse(runtime.exists())

    def test_portable_install_without_npx_fails_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            sandbox = Path(directory)
            runtime = sandbox / "runtime"
            tools_dir = sandbox / "tools"
            tools_dir.mkdir()
            (tools_dir / "dirname").symlink_to(shutil.which("dirname"))
            result = subprocess.run(
                ["/bin/bash", str(ROOT / "install.sh"), "--agent", "cursor"],
                cwd=ROOT,
                env={
                    "HOME": str(sandbox),
                    "PATH": str(tools_dir),
                    "ANYLOVER_INSTALL_ROOT": str(runtime),
                },
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("npx is required", result.stderr)
            self.assertFalse(runtime.exists())

    def test_standalone_skill_setup_dry_run_has_no_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            sandbox = Path(directory)
            result = subprocess.run(
                ["bash", str(SKILL / "scripts/setup.sh"), "--dry-run"],
                cwd=sandbox,
                env={"HOME": str(sandbox), "PATH": "/usr/bin:/bin"},
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("git+https://github.com/zifacorp/anylover.git", result.stdout)
            self.assertIn("anylover-runtime/venv/bin/anylover", result.stdout)
            self.assertEqual(list(sandbox.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
