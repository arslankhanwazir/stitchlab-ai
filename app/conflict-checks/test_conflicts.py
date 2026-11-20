"""
M4.3 Done-check Test for Conflict Detection.
Verifies:
1. Q10 flags the conflict showing both sources (D03 and D04) and both thresholds ($15,000 and $10,000).
2. ZERO false flags on Q01-Q09 (specifically checking Q02's 5 vs 10 days and Q01/Q07's durations).
3. Type 2 opposite polarity test case flags correctly.
"""

import sys
import csv
import unittest
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from app import paths
from app.retrieval.hybrid import hybrid_search
from app.retrieval.reranker import rerank
from conflicts import check_conflicts

GOLDEN_CSV = paths.REPO_ROOT / "documents" / "test-questions" / "golden-tests.csv"


class TestConflictDetection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions = {}
        with open(GOLDEN_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.questions[row["id"]] = row["question"]

    def test_q01_to_q09_zero_false_flags(self):
        """Assures Q01-Q09 produce ZERO false positive conflict flags."""
        for i in range(1, 10):
            qid = f"Q0{i}"
            q_text = self.questions[qid]
            hits = hybrid_search(q_text, top_candidates=10)
            reranked = rerank(q_text, hits)[:5]

            conflict = check_conflicts(reranked)
            self.assertIsNone(
                conflict,
                f"False positive conflict detected for {qid} ('{q_text}'):\n{conflict}",
            )

    def test_q10_flags_conflict_with_both_sources_and_thresholds(self):
        """Assures Q10 flags conflict showing both sources (D03, D04) and thresholds ($15,000, $10,000)."""
        qid = "Q10"
        q_text = self.questions[qid]
        hits = hybrid_search(q_text, top_candidates=10)
        reranked = rerank(q_text, hits)[:5]

        conflict = check_conflicts(reranked)
        self.assertIsNotNone(conflict, f"Expected conflict flag for {qid}, but got None.")

        print(f"\n[Q10 Detected Conflict Output]:\n{conflict}\n")

        # Must show both sources
        self.assertTrue("D03" in conflict, f"Expected D03 in conflict output: {conflict}")
        self.assertTrue("D04" in conflict, f"Expected D04 in conflict output: {conflict}")

        # Must show both thresholds
        self.assertTrue("$15,000" in conflict, f"Expected $15,000 in conflict output: {conflict}")
        self.assertTrue("$10,000" in conflict, f"Expected $10,000 in conflict output: {conflict}")

        # Assert exact verbatim source sentences from chunks appear in output
        self.assertIn(
            "The Marketing Director approves campaign budgets above $15,000 per month",
            conflict,
            f"Expected exact quote from D03 §2.2 in conflict output: {conflict}",
        )
        self.assertIn(
            "A campaign with a total budget above $10,000 requires Marketing Director sign-off before launch",
            conflict,
            f"Expected exact quote from D04 §2.2 in conflict output: {conflict}",
        )

        # Assert no doubled punctuation
        self.assertNotIn(".;", conflict, f"Doubled punctuation '.;' found in conflict: {conflict}")
        self.assertNotIn("..", conflict, f"Doubled punctuation '..' found in conflict: {conflict}")

    def test_type_2_opposite_polarity(self):
        """Verifies Type 2 conflict detection on synthetic opposite polarity instructions."""
        synthetic_passages = [
            {
                "doc_id": "D01",
                "section_id": "2",
                "citation": "[D01, 2]",
                "text": "Ad account admin access must be granted directly to external contractors.",
            },
            {
                "doc_id": "D03",
                "section_id": "5",
                "citation": "[D03, 5]",
                "text": "Ad account admin access must not be granted directly to external contractors.",
            },
        ]
        conflict = check_conflicts(synthetic_passages)
        self.assertIsNotNone(conflict)
        self.assertIn("Conflicting instructions", conflict)
        self.assertIn("[D01, 2]", conflict)
        self.assertIn("[D03, 5]", conflict)


if __name__ == "__main__":
    unittest.main()
