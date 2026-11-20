"""
M6B.1 Done-check Unit Test for Passage Hard Cap.
Verifies:
1. Passing 10 passages with default limit (4) returns 4 passages.
2. Passing 10 passages requesting 10 returns at most 5 passages (hard cap <= 5).
3. Passing 10 passages requesting 5 returns 5 passages.
"""

import sys
import unittest
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from passage_limiter import (
    enforce_passage_limit,
    DEFAULT_PASSAGE_LIMIT,
    HARD_PASSAGE_CAP,
)


class TestPassageLimit(unittest.TestCase):
    def setUp(self):
        # Create 10 dummy passages
        self.ten_passages = [
            {"doc_id": f"D0{i}", "section_id": str(i), "text": f"Passage {i}"}
            for i in range(1, 11)
        ]

    def test_default_limit_is_four(self):
        forwarded = enforce_passage_limit(self.ten_passages)
        self.assertEqual(len(forwarded), 4)
        self.assertEqual(len(forwarded), DEFAULT_PASSAGE_LIMIT)

    def test_passing_ten_passages_asserts_hard_cap_le_five(self):
        # Requesting 10 passages must be strictly capped at 5
        forwarded = enforce_passage_limit(self.ten_passages, limit=10)
        self.assertLessEqual(len(forwarded), 5)
        self.assertEqual(len(forwarded), HARD_PASSAGE_CAP)

    def test_requesting_five_passages(self):
        forwarded = enforce_passage_limit(self.ten_passages, limit=5)
        self.assertEqual(len(forwarded), 5)


if __name__ == "__main__":
    unittest.main()
