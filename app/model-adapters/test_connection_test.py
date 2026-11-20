"""
M6A.5 Done-check Unit Test for Connection Health Tester.
Tests all required error states and success state:
1. Invalid key (HTTP 401 -> INVALID_KEY)
2. Credit / quota exhausted (HTTP 429 -> QUOTA_EXCEEDED)
3. Network unreachable (connection refused/timeout -> NETWORK_ERROR)
4. Successful connection (HTTP 200 -> CONNECTED)
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

from connection_test import test_provider_connection


class ConfigurableMockHandler(BaseHTTPRequestHandler):
    """Mock HTTP handler with configurable response codes."""
    response_code = 200

    def log_message(self, format, *args):
        pass

    def do_POST(self):
        if ConfigurableMockHandler.response_code == 200:
            resp = {
                "choices": [{"message": {"role": "assistant", "content": "pong"}}]
            }
            body = json.dumps(resp).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif ConfigurableMockHandler.response_code == 401:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized key"}')
        elif ConfigurableMockHandler.response_code == 429:
            self.send_response(429)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Quota exceeded"}')
        else:
            self.send_response(500)
            self.end_headers()


class TestConnectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), ConfigurableMockHandler)
        cls.port = cls.server.server_port
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_invalid_key_error(self):
        ConfigurableMockHandler.response_code = 401
        res = test_provider_connection(
            provider="openai",
            api_key="sk-bad-key",
            base_url=self.base_url,
        )
        print(f"\nTested 401 -> Result: {res}")
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "INVALID_KEY")
        self.assertIn("Invalid API key", res["message"])

    def test_quota_exceeded_error(self):
        ConfigurableMockHandler.response_code = 429
        res = test_provider_connection(
            provider="openai",
            api_key="sk-quota-key",
            base_url=self.base_url,
        )
        print(f"\nTested 429 -> Result: {res}")
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "QUOTA_EXCEEDED")
        self.assertIn("quota", res["message"].lower())

    def test_network_unreachable_error(self):
        # Target an inactive port
        dead_url = "http://127.0.0.1:58888"
        res = test_provider_connection(
            provider="openai",
            api_key="sk-any-key",
            base_url=dead_url,
        )
        print(f"\nTested Unreachable -> Result: {res}")
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "NETWORK_ERROR")

    def test_successful_connection(self):
        ConfigurableMockHandler.response_code = 200
        res = test_provider_connection(
            provider="openai",
            api_key="sk-valid-key",
            base_url=self.base_url,
        )
        print(f"\nTested 200 -> Result: {res}")
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "CONNECTED")


if __name__ == "__main__":
    unittest.main()
