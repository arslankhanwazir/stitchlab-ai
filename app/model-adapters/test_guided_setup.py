"""
M6A.3 Done-check Unit Test for Guided Setup Screen.
Simulates Ollama stopped and asserts instructions show with:
- 1 download
- 2 run serve
- 3 pull llama3.2:3b
"""

import sys
import unittest
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from guided_setup import check_and_get_setup_instructions, SETUP_GUIDE_TEMPLATE


class TestGuidedSetup(unittest.TestCase):
    def test_simulated_stopped_ollama_shows_3_steps(self):
        # Simulate stopped server by querying a dead port
        instructions = check_and_get_setup_instructions(base_url="http://127.0.0.1:54321")
        self.assertIsNotNone(instructions, "Expected setup instructions when Ollama is stopped.")

        print("\n[Simulated Guided Setup Output]:\n", instructions)

        # Assert Step 1: download
        self.assertIn("1.", instructions)
        self.assertTrue(
            "Download" in instructions or "download" in instructions,
            "Expected step 1 to instruct downloading Ollama.",
        )
        self.assertIn("https://ollama.com/download", instructions)

        # Assert Step 2: run serve
        self.assertIn("2.", instructions)
        self.assertTrue(
            "serve" in instructions,
            "Expected step 2 to instruct running 'ollama serve'.",
        )

        # Assert Step 3: pull llama3.2:3b
        self.assertIn("3.", instructions)
        self.assertTrue(
            "pull" in instructions and "llama3.2:3b" in instructions,
            "Expected step 3 to instruct pulling llama3.2:3b.",
        )

    def test_running_ollama_returns_none(self):
        # When querying the actual running Ollama server
        instructions = check_and_get_setup_instructions(base_url="http://127.0.0.1:11434")
        self.assertIsNone(instructions, "Expected None when Ollama is active and responsive.")


if __name__ == "__main__":
    unittest.main()
