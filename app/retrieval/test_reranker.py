"""
M3.2 Done-check test for Cross-Encoder Reranker.
Uses stdlib unittest and csv.
Compares candidate ordering with and without reranking for Q01-Q08.
Verifies that the top chunk after reranking matches the target question.
Prints comparison tables for before and after reranking.
"""

import sys
import os
import csv
import time
import unittest
import re
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from app.retrieval.hybrid import hybrid_search
from app.retrieval.reranker import rerank

GOLDEN_CSV = paths.REPO_ROOT / "documents" / "test-questions" / "golden-tests.csv"


class TestReranker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not GOLDEN_CSV.exists():
            raise FileNotFoundError(f"golden-tests.csv not found at {GOLDEN_CSV}")
        cls.questions = []
        with open(GOLDEN_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.questions.append(row)

    def test_reranking_q01_to_q08(self):
        comparison_rows = []
        answerable = [q for q in self.questions if q["id"] in [f"Q0{i}" for i in range(1, 9)]]

        total_rerank_time = 0.0

        for q in answerable:
            qid = q["id"]
            q_text = q["question"]
            expected_sources = q["sources"]

            # Hybrid candidates (top 10)
            hybrid_hits = hybrid_search(q_text, top_candidates=10)

            t0 = time.time()
            reranked_hits = rerank(q_text, hybrid_hits)
            total_rerank_time += (time.time() - t0)

            top_hybrid = hybrid_hits[0]
            top_reranked = reranked_hits[0]

            # Verify top chunk matches the question's expected document / section
            expected_docs = re.findall(r"D0\d", expected_sources)

            # Check that top reranked chunk is from one of the expected docs
            self.assertIn(
                top_reranked["doc_id"],
                expected_docs,
                f"{qid} top reranked chunk '{top_reranked['chunk_id']}' is not in expected docs {expected_docs}",
            )

            comparison_rows.append({
                "id": qid,
                "question": q_text[:35] + ("..." if len(q_text) > 35 else ""),
                "expected": expected_sources,
                "before_top": f"{top_hybrid['chunk_id']} ({top_hybrid['citation']})",
                "before_rrf": top_hybrid["rrf_score"],
                "after_top": f"{top_reranked['chunk_id']} ({top_reranked['citation']})",
                "after_score": top_reranked["rerank_score"],
                "target_doc_match": top_reranked["doc_id"] in expected_docs,
            })

        print("\n=== M3.2 Reranking Comparison (Before vs After) ===")
        print(f"| ID | Question | Expected Source | Before (RRF Top 1) | RRF Score | After (Cross-Encoder Top 1) | CE Score | Matches Question |")
        print(f"|---|---|---|---|---|---|---|---|")
        for r in comparison_rows:
            print(f"| {r['id']} | {r['question']} | {r['expected']} | {r['before_top']} | {r['before_rrf']:.5f} | {r['after_top']} | {r['after_score']:.4f} | {'YES' if r['target_doc_match'] else 'NO'} |")

        avg_latency = total_rerank_time / len(answerable)
        print(f"\nAverage reranking latency: {avg_latency:.4f} s per query")


if __name__ == "__main__":
    unittest.main()
