from __future__ import annotations

import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from anylover.api_server import build_server
from anylover.config import Settings
from anylover.service import AnyLoverService


class APITest(unittest.TestCase):
    def test_authenticated_memory_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            service = AnyLoverService(
                Settings(data_dir=root, db_path=root / "anylover.sqlite3")
            )
            service.ensure_default_companion()
            server = build_server(service, port=0, api_token="test-token")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                connection = http.client.HTTPConnection(
                    "127.0.0.1", server.server_port, timeout=5
                )
                connection.request("GET", "/v1/memories")
                response = connection.getresponse()
                response.read()
                self.assertEqual(response.status, 401)

                body = json.dumps(
                    {
                        "content": "用户希望在移动端看到同一个伴侣",
                        "kind": "preference",
                        "consent_basis": "explicit",
                        "source_surface": "mobile",
                    },
                    ensure_ascii=False,
                ).encode()
                connection.request(
                    "POST",
                    "/v1/memories",
                    body=body,
                    headers={
                        "Authorization": "Bearer test-token",
                        "Content-Type": "application/json",
                        "Content-Length": str(len(body)),
                    },
                )
                response = connection.getresponse()
                payload = json.loads(response.read())
                self.assertEqual(response.status, 201)
                memory_id = payload["memory"]["id"]

                connection.request(
                    "GET",
                    "/v1/context?query=%E7%A7%BB%E5%8A%A8%E7%AB%AF",
                    headers={"Authorization": "Bearer test-token"},
                )
                response = connection.getresponse()
                context = json.loads(response.read())
                self.assertIn("同一个伴侣", context["prompt"])

                connection.request(
                    "DELETE",
                    f"/v1/memories/{memory_id}",
                    headers={
                        "Authorization": "Bearer test-token",
                        "X-AnyLover-Confirm": "DELETE",
                    },
                )
                response = connection.getresponse()
                deleted = json.loads(response.read())
                self.assertEqual(response.status, 200)
                self.assertTrue(deleted["deleted"])
                connection.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
