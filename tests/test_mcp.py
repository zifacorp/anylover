from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class MCPTest(unittest.TestCase):
    def test_stdio_handshake_and_memory_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            messages = [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {"protocolVersion": "2025-03-26"},
                },
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {},
                },
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "anylover_remember",
                        "arguments": {
                            "content": "用户喜欢喝乌龙茶",
                            "kind": "preference",
                            "consent_basis": "explicit",
                            "source_surface": "codex",
                        },
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "anylover_get_context",
                        "arguments": {"query": "喝什么茶"},
                    },
                },
            ]
            request_text = "".join(
                json.dumps(message, ensure_ascii=False) + "\n" for message in messages
            )
            env = os.environ.copy()
            env["ANYLOVER_HOME"] = tempdir
            src_path = str(Path(__file__).resolve().parents[1] / "src")
            env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
            result = subprocess.run(
                [sys.executable, "-m", "anylover.mcp_server"],
                input=request_text,
                text=True,
                capture_output=True,
                env=env,
                timeout=15,
                check=True,
            )
            responses = [json.loads(line) for line in result.stdout.splitlines()]
            self.assertEqual([item["id"] for item in responses], [1, 2, 3, 4])
            tools = responses[1]["result"]["tools"]
            self.assertIn("anylover_get_context", {tool["name"] for tool in tools})
            context_payload = responses[3]["result"]["structuredContent"]
            self.assertIn("用户喜欢喝乌龙茶", context_payload["prompt"])


if __name__ == "__main__":
    unittest.main()

