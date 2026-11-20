"""
M6A.4 Done-check Unit Test for Google Gemini Provider Route.
Reuses the existing OpenAIAdapter against a local fake HTTP server on 127.0.0.1.
Verifies:
1. Gemini base address (https://generativelanguage.googleapis.com/v1beta/openai/) and Bearer token header are sent.
2. Model name is not hardcoded and must be entered.
3. Connection test handles all required states: Connected, invalid key, no credit, model not found, network blocked.
4. Reads key from GEMINI_API_KEY environment variable.
"""

import os
import sys
import json
import threading
import unittest
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from openai_adapter import (
    OpenAIAdapter,
    AuthenticationError,
    QuotaExceededError,
    ModelNotFoundError,
    NetworkBlockedError,
    DEFAULT_GEMINI_URL,
)
from connection_test import test_provider_connection
from base import get_adapter


class FakeGeminiHandler(BaseHTTPRequestHandler):
    """Mock handler simulating Gemini's OpenAI-compatible endpoint."""
    last_path = None
    last_auth_header = None
    last_request_body = None

    def log_message(self, format, *args):
        pass

    def do_POST(self):
        FakeGeminiHandler.last_path = self.path
        FakeGeminiHandler.last_auth_header = self.headers.get("Authorization", "")

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        req_data = json.loads(body.decode("utf-8")) if body else {}
        FakeGeminiHandler.last_request_body = req_data

        # Path verification: base address must contain /v1beta/openai and endpoint chat/completions
        if not self.path.endswith("/v1beta/openai/chat/completions"):
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": {"code": 404, "message": "Endpoint not found"}}')
            return

        # Auth verification: Bearer token
        auth = self.headers.get("Authorization", "")
        if auth != "Bearer test-gemini-secret-key":
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": {"code": 401, "message": "API key not valid"}}')
            return

        # Model-based responses for connection testing
        model = req_data.get("model", "")
        if model == "missing-model":
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": {"code": 404, "message": "Model missing-model not found"}}')
            return
        elif model == "quota-model":
            self.send_response(429)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": {"code": 429, "message": "Quota exceeded: no credit remaining."}}')
            return

        # Successful completion response
        resp = {
            "id": "chatcmpl-gemini-fake",
            "object": "chat.completion",
            "created": 1700000000,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "According to Passage 1 [D01, 3], client onboarding follows 6 steps in ClickUp.",
                    },
                    "finish_reason": "stop",
                }
            ],
        }
        resp_bytes = json.dumps(resp).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp_bytes)))
        self.end_headers()
        self.wfile.write(resp_bytes)


class TestGeminiAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), FakeGeminiHandler)
        cls.port = cls.server.server_port
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.port}/v1beta/openai"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_gemini_base_address_and_bearer_header_sent(self):
        adapter = OpenAIAdapter(base_url=self.base_url, is_gemini=True)
        passages = [
            {"doc_id": "D01", "section_id": "3", "citation": "[D01, 3]", "text": "ClickUp onboarding steps."}
        ]

        answer = adapter.generate(
            question="What are the steps?",
            passages=passages,
            model="gemini-1.5-flash",
            api_key="test-gemini-secret-key",
        )

        print(f"\n[Test] Gemini Answer:\n{answer}")
        print(f"[Test] Request Path Sent: {FakeGeminiHandler.last_path}")
        print(f"[Test] Authorization Header: {FakeGeminiHandler.last_auth_header}")

        # Assert Gemini base address path and Bearer header
        self.assertTrue(FakeGeminiHandler.last_path.endswith("/v1beta/openai/chat/completions"))
        self.assertEqual(FakeGeminiHandler.last_auth_header, "Bearer test-gemini-secret-key")
        self.assertEqual(FakeGeminiHandler.last_request_body.get("model"), "gemini-1.5-flash")
        self.assertIn("[D01, 3]", answer)

    def test_model_name_is_not_hardcoded(self):
        # Must fail when model is None or empty for Gemini
        adapter = OpenAIAdapter(base_url=self.base_url, is_gemini=True)
        passages = [{"doc_id": "D01", "section_id": "1", "citation": "[D01, 1]", "text": "Test"}]

        with self.assertRaises(ModelNotFoundError) as ctx:
            adapter.generate(
                question="Test question",
                passages=passages,
                model=None,
                api_key="test-gemini-secret-key",
            )
        self.assertIn("Model name is required", str(ctx.exception))
        self.assertIn("use a model your key can access", str(ctx.exception))

    def test_registered_adapter_points_to_gemini_endpoint(self):
        gemini_adapter = get_adapter("gemini")
        self.assertIsInstance(gemini_adapter, OpenAIAdapter)
        self.assertEqual(gemini_adapter.base_url, "https://generativelanguage.googleapis.com/v1beta/openai")
        self.assertTrue(gemini_adapter.is_gemini)

    def test_connection_test_states(self):
        # 1. Connected state
        res_ok = test_provider_connection(
            provider="gemini",
            api_key="test-gemini-secret-key",
            model="gemini-1.5-flash",
            base_url=self.base_url,
        )
        print(f"\n[Test] Connection OK -> {res_ok}")
        self.assertTrue(res_ok["success"])
        self.assertEqual(res_ok["status"], "CONNECTED")
        self.assertEqual(res_ok["message"], "Connected")

        # 2. Invalid key state
        res_bad_key = test_provider_connection(
            provider="gemini",
            api_key="wrong-key",
            model="gemini-1.5-flash",
            base_url=self.base_url,
        )
        print(f"[Test] Connection Bad Key -> {res_bad_key}")
        self.assertFalse(res_bad_key["success"])
        self.assertEqual(res_bad_key["status"], "INVALID_KEY")
        self.assertIn("Invalid key", res_bad_key["message"])

        # 3. No credit / quota exhausted state
        res_quota = test_provider_connection(
            provider="gemini",
            api_key="test-gemini-secret-key",
            model="quota-model",
            base_url=self.base_url,
        )
        print(f"[Test] Connection No Credit -> {res_quota}")
        self.assertFalse(res_quota["success"])
        self.assertEqual(res_quota["status"], "NO_CREDIT")
        self.assertIn("No credit", res_quota["message"])

        # 4. Model not found state
        res_model_missing = test_provider_connection(
            provider="gemini",
            api_key="test-gemini-secret-key",
            model="missing-model",
            base_url=self.base_url,
        )
        print(f"[Test] Connection Model Not Found -> {res_model_missing}")
        self.assertFalse(res_model_missing["success"])
        self.assertEqual(res_model_missing["status"], "MODEL_NOT_FOUND")
        self.assertIn("Model not found", res_model_missing["message"])

        # 5. Network blocked / unreachable state
        dead_url = "http://127.0.0.1:59997/v1beta/openai"
        res_net = test_provider_connection(
            provider="gemini",
            api_key="test-gemini-secret-key",
            model="gemini-1.5-flash",
            base_url=dead_url,
        )
        print(f"[Test] Connection Network Blocked -> {res_net}")
        self.assertFalse(res_net["success"])
        self.assertEqual(res_net["status"], "NETWORK_BLOCKED")
        self.assertIn("Network blocked", res_net["message"])

    def test_environment_variable_key_support(self):
        old_env = os.environ.get("GEMINI_API_KEY")
        try:
            os.environ["GEMINI_API_KEY"] = "test-gemini-secret-key"
            res = test_provider_connection(
                provider="gemini",
                model="gemini-1.5-flash",
                base_url=self.base_url,
            )
            self.assertTrue(res["success"])
            self.assertEqual(res["status"], "CONNECTED")
        finally:
            if old_env is not None:
                os.environ["GEMINI_API_KEY"] = old_env
            else:
                os.environ.pop("GEMINI_API_KEY", None)


if __name__ == "__main__":
    unittest.main()
