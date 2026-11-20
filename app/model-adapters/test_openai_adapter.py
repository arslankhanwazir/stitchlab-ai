"""
M6A.4 Done-check Unit Test for OpenAI Adapter.
Spawns a local fake HTTP server on 127.0.0.1 using stdlib http.server.
Asserts:
1. Call succeeds against the fake server with valid bearer auth and returns completion.
2. Call fails gracefully with ConnectionError when network is unreachable.
"""

import sys
import json
import threading
import unittest
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from openai_adapter import OpenAIAdapter, AuthenticationError


class FakeOpenAIHandler(BaseHTTPRequestHandler):
    """Mock handler simulating OpenAI /chat/completions endpoint."""

    def log_message(self, format, *args):
        # Suppress server stderr logs during test
        pass

    def do_POST(self):
        if self.path.endswith("/chat/completions"):
            auth_header = self.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error": {"message": "Invalid API Key"}}')
                return

            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            req_data = json.loads(body.decode("utf-8"))

            mock_response = {
                "id": "chatcmpl-fake-12345",
                "object": "chat.completion",
                "created": 1700000000,
                "model": req_data.get("model", "gpt-4o-mini"),
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "According to Passage 1 [D03, 4], the Account Lead signs off creative before client approval.",
                        },
                        "finish_reason": "stop",
                    }
                ],
            }

            resp_bytes = json.dumps(mock_response).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
        else:
            self.send_response(404)
            self.end_headers()


class TestOpenAIAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start fake server on localhost with ephemeral port
        cls.server = HTTPServer(("127.0.0.1", 0), FakeOpenAIHandler)
        cls.port = cls.server.server_port
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_call_succeeds_against_fake_server(self):
        adapter = OpenAIAdapter(base_url=f"http://127.0.0.1:{self.port}")
        passages = [
            {"doc_id": "D03", "section_id": "4", "citation": "[D03, 4]", "text": "Creative sign-off."}
        ]
        q = "Who signs off creative?"
        ans = adapter.generate(q, passages, api_key="sk-fake-valid-key")
        print(f"\nFake OpenAI Response:\n{ans}")

        self.assertIn("[D03, 4]", ans)
        self.assertIn("Account Lead", ans)

    def test_fails_gracefully_without_network(self):
        # Point to a dead/unbound port
        adapter = OpenAIAdapter(base_url="http://127.0.0.1:59999")
        passages = [{"doc_id": "D01", "section_id": "1", "citation": "[D01, 1]", "text": "Test"}]

        with self.assertRaises(ConnectionError) as ctx:
            adapter.generate("Question", passages, api_key="sk-fake-key", timeout=0.5)

        print(f"\nGraceful Connection Error Caught:\n{ctx.exception}")
        self.assertIn("Network unreachable", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
