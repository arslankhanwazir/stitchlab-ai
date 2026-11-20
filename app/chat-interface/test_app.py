"""
M5.1 Done-check Test for Gradio Interface.
Starts the app, sends a question, asserts an answer is returned, then stops the app.
"""

import sys
import time
import unittest
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

import importlib.util
app_path = Path(__file__).resolve().parent / "app.py"
spec = importlib.util.spec_from_file_location("chat_interface_app", app_path)
chat_app = importlib.util.module_from_spec(spec)
sys.modules["chat_interface_app"] = chat_app
spec.loader.exec_module(chat_app)
create_app = chat_app.create_app
chat_respond = chat_app.chat_respond


class TestGradioApp(unittest.TestCase):
    def test_app_lifecycle_and_response(self):
        print("\nStarting Gradio app test...")
        demo = create_app()

        # Launch non-blocking on local port
        demo.launch(
            server_name="127.0.0.1",
            server_port=7865,
            prevent_thread_lock=True,
            show_error=True,
        )
        print("Gradio app launched on http://127.0.0.1:7865.")

        try:
            # Send question through handler
            question = "What are the steps to onboard a new client in ClickUp?"
            answer, conflict, citations, passages, audit_json = chat_respond(question)

            print(f"Returned Answer:\n{answer[:120]}...")
            print(f"Returned Citations: {citations}")

            self.assertTrue(len(answer) > 0, "Expected non-empty answer from app.")
            self.assertIn("D01", citations, "Expected citation to D01.")
            self.assertTrue(
                "ClickUp" in answer or "Space" in answer or "contract" in answer,
                "Expected relevant onboarding keywords in answer.",
            )

            # Test conflict question: answer box must state dependence on conflicting rules and not be empty
            q_conflict = "Does a paid social campaign with a $12,000 budget need Marketing Director approval?"
            c_answer, c_banner, c_citations, c_passages, c_audit = chat_respond(q_conflict)
            print(f"\nConflict Answer Box Output:\n{c_answer}")
            print(f"Conflict Banner Output:\n{c_banner}")
            self.assertTrue(len(c_answer) > 0, "Conflict answer box must not be empty.")
            self.assertIn("depends on conflicting", c_answer.lower(), "Answer must state that it depends on conflicting rules.")
            self.assertTrue(len(c_banner) > 0, "Conflict banner must not be empty.")

            # Assert exact source sentences appear in answer and banner
            self.assertIn(
                "The Marketing Director approves campaign budgets above $15,000 per month",
                c_answer,
                "Expected exact quote from D03 §2.2 in conflict answer box.",
            )
            self.assertIn(
                "A campaign with a total budget above $10,000 requires Marketing Director sign-off before launch",
                c_answer,
                "Expected exact quote from D04 §2.2 in conflict answer box.",
            )
        finally:
            print("Stopping Gradio app...")
            demo.close()
            print("Gradio app stopped cleanly.")


if __name__ == "__main__":
    unittest.main()
