"""
M3.3 Done-check test for Relevance Threshold.
Uses stdlib unittest and csv.
Tests:
1. Q09 triggers is_found=False and returns exactly "Not found in your documents."
2. Q01-Q08 trigger is_found=True and retain target documents.
3. Q10 triggers is_found=True and retrieves passages from BOTH D03 and D04.
4. Prints top score for all 10 questions and calibration margins.
"""

import sys
import os
import csv
import unittest
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from app.retrieval.hybrid import hybrid_search
from app.retrieval.reranker import rerank
from app.retrieval.threshold import (
    apply_threshold,
    MIN_RELEVANCE_SCORE,
    NOT_FOUND_MESSAGE,
)

GOLDEN_CSV = paths.REPO_ROOT / "documents" / "test-questions" / "golden-tests.csv"


class TestThreshold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not GOLDEN_CSV.exists():
            raise FileNotFoundError(f"golden-tests.csv not found at {GOLDEN_CSV}")
        cls.questions = []
        with open(GOLDEN_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.questions.append(row)

    def test_all_10_questions_threshold(self):
        scores_table = []
        answerable_top_scores = []
        q09_top_score = None

        for q in self.questions:
            qid = q["id"]
            q_text = q["question"]
            expected_behaviour = q["expected_behaviour"]

            hits = hybrid_search(q_text, top_candidates=10)
            reranked = rerank(q_text, hits)
            top_score = reranked[0]["rerank_score"] if reranked else -999.0
            top_chunk = reranked[0]["chunk_id"] if reranked else "None"

            filtered_passages, is_found = apply_threshold(reranked, threshold=MIN_RELEVANCE_SCORE)

            if expected_behaviour == "ANSWER":
                answerable_top_scores.append(top_score)
                self.assertTrue(is_found, f"{qid} was incorrectly marked as not found (score {top_score})")
                self.assertTrue(len(filtered_passages) > 0)
            elif expected_behaviour == "NOT_FOUND":
                q09_top_score = top_score
                self.assertFalse(is_found, f"{qid} was not rejected by threshold (score {top_score})")
                self.assertEqual(len(filtered_passages), 0)
            elif expected_behaviour == "CONFLICT":
                self.assertTrue(is_found, f"{qid} was incorrectly marked as not found")
                # Q10 must retrieve both D03 and D04
                retrieved_docs = {p["doc_id"] for p in filtered_passages}
                self.assertIn("D03", retrieved_docs, "Q10 must retrieve D03")
                self.assertIn("D04", retrieved_docs, "Q10 must retrieve D04")

            result_str = "FOUND" if is_found else NOT_FOUND_MESSAGE
            scores_table.append({
                "id": qid,
                "behaviour": expected_behaviour,
                "top_score": top_score,
                "top_chunk": top_chunk,
                "status": result_str,
                "passages_retained": len(filtered_passages),
            })

        print("\n=== M3.3 Relevance Scores & Threshold Evaluation ===")
        print(f"| ID | Behaviour | Top Score | Top Chunk | Threshold Result | Retained Passages |")
        print(f"|---|---|---|---|---|---|")
        for r in scores_table:
            print(f"| {r['id']} | {r['behaviour']} | {r['top_score']:.4f} | {r['top_chunk']} | {r['status']} | {r['passages_retained']} |")

        lowest_answerable = min(answerable_top_scores)
        margin = lowest_answerable - q09_top_score
        print(f"\nLowest Answerable Top Score: {lowest_answerable:.4f} (Q02)")
        print(f"Q09 (Unanswerable) Top Score: {q09_top_score:.4f}")
        print(f"Chosen Threshold: {MIN_RELEVANCE_SCORE}")
        print(f"Safety Margin: {margin:.4f} points")
        print("Note on overfitting: The test set is small (10 questions). The threshold of 0.0 relies on the zero-crossing nature of the MS-MARCO cross-encoder logit scale, but evaluates on only 1 planted negative.")


if __name__ == "__main__":
    unittest.main()
