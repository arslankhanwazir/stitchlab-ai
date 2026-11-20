"""
M4.1 Done-check test for Evidence-only Answers.
Uses stdlib unittest, csv, json, re.
Runs Q01-Q08 through hybrid retrieval + reranking + Ollama llama3.2:3b.
Checks:
- Answers cite the correct section (e.g. [D01, 3] or [D01, 3.3])
- Answers contain the key facts (evaluated against documents/test-questions/golden-checks.json)
Saves raw answers to docs/project-record/m4-sample-outputs.md.
"""

import sys
import os
import csv
import json
import re
import unittest
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from app.retrieval.hybrid import hybrid_search
from app.retrieval.reranker import rerank
from app.retrieval.threshold import apply_threshold
from app.citations.answer import generate_answer

GOLDEN_CSV = paths.REPO_ROOT / "documents" / "test-questions" / "golden-tests.csv"
CHECKS_JSON = paths.REPO_ROOT / "documents" / "test-questions" / "golden-checks.json"
SAMPLE_OUTPUTS_MD = paths.REPO_ROOT / "docs" / "project-record" / "m4-sample-outputs.md"


class TestAnswerGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not GOLDEN_CSV.exists():
            raise FileNotFoundError(f"golden-tests.csv not found at {GOLDEN_CSV}")
        if not CHECKS_JSON.exists():
            raise FileNotFoundError(f"golden-checks.json not found at {CHECKS_JSON}")

        cls.questions = []
        with open(GOLDEN_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.questions.append(row)

        with open(CHECKS_JSON, mode="r", encoding="utf-8") as f:
            cls.checks = json.load(f)

    def test_q01_to_q08_answers(self):
        answerable = [q for q in self.questions if q["id"] in [f"Q0{i}" for i in range(1, 9)]]
        markdown_sections = ["# M4.1 Sample Outputs and Citation Verifications\n\nGenerated with `llama3.2:3b` at temperature 0.\n"]

        results_summary = []

        for q in answerable:
            qid = q["id"]
            q_text = q["question"]
            expected_answer = q["expected_answer"]
            check_rule = self.checks.get(qid, {})

            print(f"\nEvaluating {qid}: {q_text}")

            # 1. Retrieve candidates
            hits = hybrid_search(q_text, top_candidates=10)
            reranked = rerank(q_text, hits)
            passages = reranked[:5]

            # 2. Generate answer
            answer = generate_answer(q_text, passages)
            print(f"  Answer: {answer}")

            # 3. Check citations
            expected_cits = check_rule.get("expected_citations", [])
            # Citation check: looks for doc and section, e.g. [D01, 3] or D01, 3.3
            cit_found = False
            for exp_c in expected_cits:
                parts = exp_c.split(",")
                d_id = parts[0].strip()
                s_id = parts[1].strip()
                pat = rf"\[?\b{d_id}\b.*?\b{s_id}\b.*?\]?"
                if re.search(pat, answer):
                    cit_found = True
                    break

            self.assertTrue(
                cit_found,
                f"{qid} citation missing! Expected one of {expected_cits}. Got answer:\n{answer}",
            )

            # 4. Check key facts (regexes)
            regex_patterns = check_rule.get("required_regex", [])
            missing_regex = []
            for pat in regex_patterns:
                if not re.search(pat, answer):
                    missing_regex.append(pat)

            self.assertEqual(
                len(missing_regex),
                0,
                f"{qid} missing required facts: {missing_regex}. Got answer:\n{answer}",
            )

            results_summary.append({
                "id": qid,
                "question": q_text,
                "answer": answer,
                "citation_pass": cit_found,
                "facts_pass": len(missing_regex) == 0,
            })

            # Append to sample outputs document
            markdown_sections.append(f"## {qid}: {q_text}\n")
            markdown_sections.append(f"**Expected Answer:** {expected_answer}  \n")
            markdown_sections.append(f"**Retrieved Passages:** {', '.join(p['citation'] for p in passages)}  \n")
            markdown_sections.append(f"**Generated Answer:**\n> {answer}\n")
            markdown_sections.append(f"**Citation Verified:** {'YES' if cit_found else 'NO'} | **Key Facts Verified:** {'YES' if len(missing_regex) == 0 else 'NO'}\n\n---\n")

            # Progressive write to m4-sample-outputs.md
            SAMPLE_OUTPUTS_MD.write_text("\n".join(markdown_sections), encoding="utf-8")
        print(f"\nRaw sample outputs saved to: {SAMPLE_OUTPUTS_MD}")


if __name__ == "__main__":
    unittest.main()
