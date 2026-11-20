"""
M6A.2 Done-check Unit Test for Ollama Adapter.
Verifies detection of running Ollama, listing installed models, and prompt execution.
"""

import sys
import unittest
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from base import get_answer
from ollama_adapter import (
    is_ollama_running,
    list_installed_models,
    OllamaAdapter,
)


class TestOllamaAdapter(unittest.TestCase):
    def test_detect_running_ollama(self):
        running = is_ollama_running("http://127.0.0.1:11434")
        self.assertTrue(running, "Expected Ollama to be running on 127.0.0.1:11434")

    def test_detect_stopped_ollama(self):
        # Unused port should report False
        running = is_ollama_running("http://127.0.0.1:54321", timeout=0.5)
        self.assertFalse(running, "Expected stopped service to report False")

    def test_list_installed_models(self):
        models = list_installed_models("http://127.0.0.1:11434")
        print(f"\nInstalled Ollama models: {models}")
        self.assertIsInstance(models, list)
        self.assertTrue(len(models) > 0, "Expected at least one installed model.")
        has_llama32 = any("llama3.2:3b" in m for m in models)
        self.assertTrue(has_llama32, "Expected llama3.2:3b to be listed among installed models.")

    def test_send_prompt_via_adapter(self):
        passages = [
            {
                "doc_id": "D02",
                "section_id": "4",
                "section_title": "Approval rules",
                "citation": "[D02, 4]",
                "text": "## 4. Approval rules\n\n4.1 The Account Lead reviews the refund request.\n\n4.2 Approval decisions are made within 5 working days of receiving a complete request.",
            }
        ]
        q = "How long does an enterprise refund approval take?"
        ans = get_answer(q, passages, provider="ollama", model="llama3.2:3b")
        print(f"\nOllama Answer:\n{ans}")
        self.assertIn("5 working days", ans)
        self.assertIn("D02", ans)


if __name__ == "__main__":
    unittest.main()
