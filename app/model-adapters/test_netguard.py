"""
M6B.3 Done-check Unit Test for Outbound Network Guard.
Verifies:
1. Allows 127.0.0.1:11434 (local Ollama).
2. Allows active provider host (e.g. api.openai.com).
3. Allows generativelanguage.googleapis.com ONLY when Gemini is the chosen provider.
4. Blocks arbitrary url like evil.com.
5. Blocks loopback on wrong port like 127.0.0.1:9999.
"""

import sys
import unittest
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from netguard import is_url_allowed, validate_outbound_url


class TestNetGuard(unittest.TestCase):
    def test_allows_local_ollama_port(self):
        # Must allow 127.0.0.1:11434 and localhost:11434
        self.assertTrue(is_url_allowed("http://127.0.0.1:11434/api/chat"))
        self.assertTrue(is_url_allowed("http://localhost:11434/api/tags"))
        validate_outbound_url("http://127.0.0.1:11434/api/chat")

    def test_allows_active_provider_host(self):
        active_host = "api.openai.com"
        # Must allow active provider
        self.assertTrue(
            is_url_allowed(
                "https://api.openai.com/v1/chat/completions",
                active_provider_host=active_host,
            )
        )
        validate_outbound_url(
            "https://api.openai.com/v1/chat/completions",
            active_provider_host=active_host,
        )

    def test_gemini_host_allowed_only_when_gemini_chosen(self):
        gemini_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

        # Allowed when Gemini is the chosen provider
        self.assertTrue(is_url_allowed(gemini_url, active_provider="gemini"))
        self.assertTrue(
            is_url_allowed(
                gemini_url,
                active_provider="gemini",
                active_provider_host="generativelanguage.googleapis.com",
            )
        )
        validate_outbound_url(gemini_url, active_provider="gemini")

        # BLOCKED when no provider is specified (e.g. local mode)
        self.assertFalse(is_url_allowed(gemini_url))
        with self.assertRaises(PermissionError):
            validate_outbound_url(gemini_url)

        # BLOCKED when another provider is chosen (e.g. openai or ollama)
        self.assertFalse(is_url_allowed(gemini_url, active_provider="openai"))
        self.assertFalse(is_url_allowed(gemini_url, active_provider="ollama"))
        with self.assertRaises(PermissionError):
            validate_outbound_url(gemini_url, active_provider="openai")
        with self.assertRaises(PermissionError):
            validate_outbound_url(gemini_url, active_provider="ollama")

    def test_blocks_arbitrary_urls(self):
        # Must block arbitrary external domains
        self.assertFalse(is_url_allowed("http://evil.com/exfiltrate"))
        self.assertFalse(is_url_allowed("https://evil.com/steal-data"))
        self.assertFalse(is_url_allowed("https://unapproved-api.example.com"))

        with self.assertRaises(PermissionError):
            validate_outbound_url("http://evil.com")

    def test_blocks_loopback_on_wrong_port(self):
        # Must block loopback ports other than 11434
        self.assertFalse(is_url_allowed("http://127.0.0.1:9999"))
        self.assertFalse(is_url_allowed("http://localhost:8080/admin"))
        self.assertFalse(is_url_allowed("http://127.0.0.1:3000"))

        with self.assertRaises(PermissionError):
            validate_outbound_url("http://127.0.0.1:9999")


if __name__ == "__main__":
    unittest.main()
