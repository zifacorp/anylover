from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PortableCLITest(unittest.TestCase):
    def test_cross_surface_memory_flow_without_mcp(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = {
                **os.environ,
                "ANYLOVER_HOME": directory,
                "ANYLOVER_DB": str(Path(directory) / "memory.sqlite3"),
                "PYTHONPATH": str(ROOT / "src"),
                "ANYLOVER_USER_ID": "portable-test",
                "ANYLOVER_COMPANION_ID": "default",
            }

            def cli(*args: str) -> dict:
                result = subprocess.run(
                    [sys.executable, "-m", "anylover", *args],
                    env=env,
                    cwd=directory,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                return json.loads(result.stdout)

            # The portable Skill must work outside the source checkout and
            # retain the actual agent surface through a shared CLI database.
            cli("init", "--name", "Portable Any", "--persona", "Keep this persona")
            session = cli("session", "--surface", "cursor", "--external-id", "test-1")
            saved = cli(
                "remember", "--kind", "preference", "--consent", "explicit",
                "--surface", "cursor", "--session-id", session["session_id"],
                "--", "I prefer short explanations; keep $HOME and `quotes` literal.",
            )["memory"]
            context = cli("context", "--query", "short explanations", "--json")
            self.assertEqual(context["companion"]["display_name"], "Portable Any")
            self.assertEqual(context["memories"][0]["source_surface"], "cursor")
            self.assertEqual(context["memories"][0]["content"], saved["content"])

            replacement = cli(
                "remember", "--kind", "preference", "--consent", "explicit",
                "--surface", "windsurf", "--supersedes", saved["id"],
                "--", "I now prefer detailed explanations.",
            )["memory"]
            self.assertEqual(cli("list", "--json")["memories"][0]["id"], replacement["id"])
            cli("forget", replacement["id"], "--confirm", "DELETE")
            self.assertEqual(cli("list", "--json")["memories"], [])
            self.assertEqual(cli("companion")["persona"], "Keep this persona")


if __name__ == "__main__":
    unittest.main()
