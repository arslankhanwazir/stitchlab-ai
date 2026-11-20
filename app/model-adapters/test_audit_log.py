"""
M6B.4 Done-check Unit Test for What-Was-Sent Log.
Asserts:
1. Query execution creates log entry in logs/what-was-sent.jsonl.
2. Log entry matches what was sent.
3. Zero raw unmasked PII appears in the log.
"""

import sys
import json
import unittest
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from masking import mask_data
from audit_log import log_what_was_sent, read_latest_audit_entry, AUDIT_LOG_FILE


class TestAuditLog(unittest.TestCase):
    def setUp(self):
        # Use a temporary test log file to keep test isolated
        self.test_log_path = paths.REPO_ROOT / "logs" / "test-what-was-sent.jsonl"
        if self.test_log_path.exists():
            self.test_log_path.unlink()

    def tearDown(self):
        if self.test_log_path.exists():
            self.test_log_path.unlink()

    def test_log_entry_matches_and_contains_no_unmasked_pii(self):
        # Raw passage containing PII
        raw_text = (
            "| Platform or server outage | Sam Whitfield, Systems Lead (on-call) | "
            "sam.whitfield@brightpath-demo.example | +1 555 0177 |"
        )
        # Apply data masking before sending/logging
        masked_text, mapping = mask_data(raw_text)

        masked_passages = [
            {
                "doc_id": "D05",
                "section_id": "1",
                "citation": "[D05, 1]",
                "text": masked_text,
            }
        ]
        q = "Who is the on-call contact for server outages?"

        # Log what was sent
        entry = log_what_was_sent(
            question=q,
            passages=masked_passages,
            provider="openai",
            model="gpt-4o-mini",
            endpoint="https://api.openai.com/v1/chat/completions",
            log_file_path=self.test_log_path,
        )

        print("\n=== RECORDED AUDIT ENTRY ===")
        print(json.dumps(entry, indent=2))

        # Assert 1: Log file exists and latest entry read matches
        self.assertTrue(self.test_log_path.exists())
        latest = read_latest_audit_entry(log_file_path=self.test_log_path)
        self.assertIsNotNone(latest)
        self.assertEqual(latest["question"], q)
        self.assertEqual(latest["provider"], "openai")
        self.assertEqual(latest["model"], "gpt-4o-mini")

        # Assert 2: Entry prompt matches what was sent
        logged_prompt = latest["full_prompt_sent"]
        self.assertIn(q, logged_prompt)
        self.assertIn("[D05, 1]", logged_prompt)
        self.assertIn("[PERSON_NAME_1]", logged_prompt)
        self.assertIn("[PHONE_NUM_1]", logged_prompt)

        # Assert 3: No raw unmasked PII in the log
        log_file_raw_content = self.test_log_path.read_text(encoding="utf-8")
        self.assertNotIn("Sam Whitfield", log_file_raw_content)
        self.assertNotIn("+1 555 0177", log_file_raw_content)
        self.assertNotIn("sam.whitfield@brightpath-demo.example", log_file_raw_content)
        print("\nVerified: Zero unmasked PII present in audit log.")


if __name__ == "__main__":
    unittest.main()
