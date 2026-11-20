"""
M3.1 Done-check test for Hybrid search.
Uses stdlib unittest and csv.
Tests Q01-Q08 from golden-tests.csv.
Asserts that for each question, a chunk from the expected document appears in the top results.
Prints a formatted table including question ID, question text, expected document, retrieved top chunk, and its rank.
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

GOLDEN_CSV = paths.REPO_ROOT / "documents" / "test-questions" / "golden-tests.csv"


class TestHybridSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assertTrue(GOLDEN_CSV.exists(), f"golden-tests.csv not found at {GOLDEN_CSV}")
        cls.questions = []
        with open(GOLDEN_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.questions.append(row)

    def test_q01_to_q08_retrieval(self):
        """Verifies Q01-Q08 retrieve at least one chunk from the expected document in the top results."""
        table_rows = []
        answerable_questions = [q for q in self.questions if q["id"] in [f"Q0{i}" for i in range(1, 9)]]

        for q in answerable_questions:
            qid = q["id"]
            q_text = q["question"]
            expected_src = q["sources"]  # e.g. "D01 section 3.3" or "D03 sections 4.1 and 4.2"
            
            # Extract expected doc IDs (e.g. ['D01'] or ['D06', 'D07'])
            import re
            expected_docs = re.findall(r"D0\d", expected_src)

            hits = hybrid_search(q_text, top_candidates=10)
            self.assertTrue(len(hits) > 0, f"No hits returned for {qid}")

            retrieved_docs = [h["doc_id"] for h in hits]
            
            # Find the best rank of an expected doc
            matching_ranks = [h["hybrid_rank"] for h in hits if h["doc_id"] in expected_docs]
            self.assertTrue(
                len(matching_ranks) > 0,
                f"{qid} ('{q_text}') failed to retrieve any chunk from expected doc(s) {expected_docs}. Retrieved: {retrieved_docs}",
            )

            best_rank = matching_ranks[0]
            top_hit = hits[0]
            best_matching_hit = next(h for h in hits if h["doc_id"] in expected_docs)

            table_rows.append({
                "id": qid,
                "question": q_text[:40] + ("..." if len(q_text) > 40 else ""),
                "expected": ", ".join(expected_docs),
                "top_hit_chunk": top_hit["chunk_id"],
                "top_hit_cit": top_hit["citation"],
                "best_match_chunk": best_matching_hit["chunk_id"],
                "best_match_rank": best_rank,
                "rrf_score": best_matching_hit["rrf_score"],
            })

            # Assert expected doc is within top 5 results
            self.assertLessEqual(
                best_rank,
                5,
                f"{qid} best matching rank {best_rank} exceeds top-5 threshold",
            )

        # Print formatted markdown table
        print("\n=== M3.1 Hybrid Search Results (Q01 - Q08) ===")
        print(f"| ID | Question | Expected Doc | Top Hit | Best Expected Hit | Best Rank | RRF Score |")
        print(f"|---|---|---|---|---|---|---|")
        for r in table_rows:
            print(f"| {r['id']} | {r['question']} | {r['expected']} | {r['top_hit_chunk']} ({r['top_hit_cit']}) | {r['best_match_chunk']} | Rank {r['best_match_rank']} | {r['rrf_score']:.5f} |")


if __name__ == "__main__":
    unittest.main()
