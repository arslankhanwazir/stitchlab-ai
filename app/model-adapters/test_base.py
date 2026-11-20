"""
M6A.1 Done-check Unit Test for Unified Provider Adapter Interface.
Tests base interface, registry, and stub adapter.
"""

import sys
import unittest
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from base import (
    BaseModelAdapter,
    StubAdapter,
    get_answer,
    get_adapter,
    register_adapter,
)


class TestBaseAdapter(unittest.TestCase):
    def test_stub_adapter_generation(self):
        passages = [
            {"doc_id": "D01", "section_id": "3", "citation": "[D01, 3]", "text": "Step 1..."}
        ]
        q = "What are the steps?"
        ans = get_answer(q, passages, provider="stub")
        self.assertIn("[D01, 3]", ans)
        self.assertIn("What are the steps?", ans)

    def test_stub_adapter_empty_passages(self):
        ans = get_answer("Any question?", [], provider="stub")
        self.assertEqual(ans, "Not found in your documents.")

    def test_custom_stub_response(self):
        custom_stub = StubAdapter(stub_response="Custom test response [D05, 1].")
        register_adapter("custom_mock", custom_stub)

        ans = get_answer("Who to call?", [], provider="custom_mock")
        self.assertEqual(ans, "Custom test response [D05, 1].")

    def test_unsupported_provider_raises_error(self):
        with self.assertRaises(ValueError):
            get_answer("Question", [], provider="unknown_provider_xyz")


if __name__ == "__main__":
    unittest.main()
