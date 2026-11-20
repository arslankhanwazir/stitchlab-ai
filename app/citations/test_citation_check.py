"""
M4.2: Citation Check Test Suite.
Verifies:
- Normalization of variants ([D03, 2], [D03, §2], [D03, Section 2.2], [D03, 2.2])
- Real citations passing verification
- Fake citations flagged and replaced with error note
"""

import sys
import unittest
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from app import paths

from app.citations.citation_check import (
    normalize_citation,
    verify_and_filter_citations,
)


class TestCitationCheck(unittest.TestCase):
    def test_normalization_variants(self):
        cases = [
            ("D03", "2", ("D03", "2")),
            ("d03", "2", ("D03", "2")),
            ("D03", "§2", ("D03", "2")),
            ("D03", "Section 2.2", ("D03", "2")),
            ("D03", "2.2", ("D03", "2")),
            ("D01", "Sec. 3.3", ("D01", "3")),
            ("D04", "1", ("D04", "1")),
        ]
        for doc_in, sec_in, expected in cases:
            norm_doc, norm_sec = normalize_citation(doc_in, sec_in)
            self.assertEqual((norm_doc, norm_sec), expected, f"Failed for ({doc_in}, {sec_in})")

    def test_real_citations_pass(self):
        retrieved_passages = [
            {"doc_id": "D03", "section_id": "4", "citation": "[D03, 4]"},
            {"doc_id": "D04", "section_id": "1", "citation": "[D04, 1]"},
            {"doc_id": "D01", "section_id": "3", "citation": "[D01, 3]"},
        ]

        sample_answer = (
            "According to [D03, 4], the Account Lead signs off creative. "
            "See also [D04, Section 1] and [D01, 3.3] for details."
        )

        sanitized, records, all_valid = verify_and_filter_citations(sample_answer, retrieved_passages)

        self.assertTrue(all_valid, "Expected all real citations to be valid.")
        self.assertEqual(len(records), 3)
        for r in records:
            self.assertTrue(r["is_valid"], f"Record failed: {r}")

        # The answer should not contain any INVALID CITATION notes
        self.assertNotIn("INVALID CITATION", sanitized)

    def test_fake_citations_flagged_and_replaced(self):
        retrieved_passages = [
            {"doc_id": "D03", "section_id": "4", "citation": "[D03, 4]"},
        ]

        sample_answer_with_fake = (
            "According to [D03, 4], the Account Lead signs off creative. "
            "However, [D99, 1] claims something else, and [D02, 3] discusses refunds."
        )

        sanitized, records, all_valid = verify_and_filter_citations(sample_answer_with_fake, retrieved_passages)

        self.assertFalse(all_valid, "Expected fake/unretrieved citations to be flagged as invalid.")
        self.assertEqual(len(records), 3)

        # First citation should be valid
        self.assertTrue(records[0]["is_valid"])
        self.assertEqual(records[0]["doc_id"], "D03")

        # Second and third citations are invalid
        self.assertFalse(records[1]["is_valid"])
        self.assertEqual(records[1]["doc_id"], "D99")
        self.assertFalse(records[2]["is_valid"])
        self.assertEqual(records[2]["doc_id"], "D02")

        # Check sanitized string replacement
        self.assertIn("[INVALID CITATION: D99, 1]", sanitized)
        self.assertIn("[INVALID CITATION: D02, 3]", sanitized)
        self.assertIn("[D03, 4]", sanitized)
        print("\nSanitized Answer Output with Fake Citations:")
        print(sanitized)


if __name__ == "__main__":
    unittest.main()
