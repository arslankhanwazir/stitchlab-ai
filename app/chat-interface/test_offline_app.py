"""
M5.1: Network-Blocked Offline Startup and Execution Test.
Starts the Gradio app with all external network access strictly blocked,
verifies that no models are downloaded, and confirms the app still answers queries.
"""

import os
import sys
import time
import socket
import unittest
from pathlib import Path

# Enforce offline mode and telemetry disablement prior to any library imports
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

# Ensure app and subfolders are registered on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
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

ALLOWED_HOSTS = {"127.0.0.1", "localhost", "::1", "0.0.0.0", None, ""}


class TestOfflineAppWithNetworkBlocked(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Save original socket methods
        cls.orig_getaddrinfo = socket.getaddrinfo
        cls.orig_connect = socket.socket.connect
        cls.blocked_calls = []

        def blocked_getaddrinfo(host, port, *args, **kwargs):
            if host not in ALLOWED_HOSTS:
                cls.blocked_calls.append(("getaddrinfo", host, port))
                raise socket.gaierror(-3, f"External network blocked by test: {host}")
            return cls.orig_getaddrinfo(host, port, *args, **kwargs)

        def blocked_connect(sock, address):
            host = address[0] if isinstance(address, tuple) else address
            if host not in ALLOWED_HOSTS:
                cls.blocked_calls.append(("connect", host))
                raise OSError(10051, f"External connection blocked by test: {host}")
            return cls.orig_connect(sock, address)

        socket.getaddrinfo = blocked_getaddrinfo
        socket.socket.connect = blocked_connect

    @classmethod
    def tearDownClass(cls):
        # Restore original socket methods
        socket.getaddrinfo = cls.orig_getaddrinfo
        socket.socket.connect = cls.orig_connect

    def test_network_blocker_blocks_external_hosts(self):
        """Verifies our blocker intercepts and forbids remote hosts."""
        with self.assertRaises(socket.gaierror):
            socket.getaddrinfo("huggingface.co", 443)
        with self.assertRaises(socket.gaierror):
            socket.getaddrinfo("api.openai.com", 443)

    def test_app_starts_and_answers_with_network_blocked(self):
        """Starts the Gradio app with network blocked, answers queries, and confirms offline success."""
        print("\n[Offline Test] Launching Gradio app with external network blocked...")
        demo = create_app()

        # Launch on local loopback only
        demo.launch(
            server_name="127.0.0.1",
            server_port=7867,
            prevent_thread_lock=True,
            show_error=True,
        )
        print("[Offline Test] Gradio app running at http://127.0.0.1:7867 (Loopback only).")

        try:
            # Test Query 1: Policy question requiring evidence retrieval and local LLM generation
            query = "What are the steps to onboard a new client in ClickUp?"
            print(f"[Offline Test] Sending query: '{query}'")
            t0 = time.time()
            answer, conflict, citations, passages, audit_json = chat_respond(query)
            elapsed = time.time() - t0
            print(f"[Offline Test] Received answer in {elapsed:.2f}s:")
            print(f"  Answer snippet: {answer[:140]}...")
            print(f"  Citations: {citations}")

            self.assertTrue(len(answer) > 0, "Expected non-empty answer from app.")
            self.assertIn("D01", citations, "Expected citation to D01.")
            self.assertTrue(
                "ClickUp" in answer or "Space" in answer or "contract" in answer,
                "Expected onboarding details in answer.",
            )

            # Test Query 2: Policy conflict query (deterministic detection)
            q_conflict = "Does a paid social campaign with a $12,000 budget need Marketing Director approval?"
            print(f"[Offline Test] Sending conflict query: '{q_conflict}'")
            c_answer, c_banner, c_citations, c_passages, c_audit = chat_respond(q_conflict)
            print(f"  Conflict answer snippet: {c_answer[:140]}...")
            self.assertEqual(
                c_answer,
                "The answer depends on the conflicting policy rules shown above. Review both documents before acting.",
            )
            self.assertTrue(len(c_banner) > 0, "Expected conflict banner.")

            # Assert exact source sentences appear verbatim in banner
            self.assertIn(
                "The Marketing Director approves campaign budgets above $15,000 per month",
                c_banner,
                "Expected exact quote from D03 §2.2 in offline test banner.",
            )
            self.assertIn(
                "A campaign with a total budget above $10,000 requires Marketing Director sign-off before launch",
                c_banner,
                "Expected exact quote from D04 §2.2 in offline test banner.",
            )

            print("[Offline Test] All queries successfully answered 100% offline.")
        finally:
            print("[Offline Test] Shutting down Gradio app...")
            demo.close()
            print("[Offline Test] Gradio app stopped cleanly.")


if __name__ == "__main__":
    unittest.main()
