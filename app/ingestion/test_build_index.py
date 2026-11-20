"""
M2.3 Done-check test for local indexes.
Uses stdlib unittest.
Runs simple probe queries (one per document, not from golden questions)
and asserts that at least one correct chunk is returned for each of D01-D07
from both the Chroma vector index and SQLite FTS5 index.
"""

import sys
import os
import re
import unittest
import sqlite3
from pathlib import Path

# Set telemetry off
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Add paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from sentence_transformers import SentenceTransformer
import chromadb
from app.ingestion.build_index import (
    CHROMA_DIR,
    FTS_PATH,
    COLLECTION_NAME,
    MODEL_NAME,
    check_fts5_support,
)

PROBES = [
    ("D01", "onboarding tasks intake meeting ClickUp space kickoff"),
    ("D02", "enterprise refund request finance approval payment window"),
    ("D03", "campaign approval rules creative sign-off budget threshold"),
    ("D04", "paid social brief template fields objective deliverables"),
    ("D05", "escalation contacts out-of-hours server outage phone numbers"),
    ("D06", "retainer pricing cancellation notice monthly fee included hours"),
    ("D07", "client faq working with us general questions answers"),
]


class TestLocalIndexes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assertTrue(check_fts5_support(), "SQLite FTS5 must be supported")
        cls.assertTrue(CHROMA_DIR.exists(), "Chroma directory must exist")
        cls.assertTrue(FTS_PATH.exists(), "SQLite FTS5 file must exist")

        cls.embed_model = SentenceTransformer(MODEL_NAME)
        cls.chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        cls.collection = cls.chroma_client.get_collection(COLLECTION_NAME)

    def test_fts5_probes(self):
        """Tests that FTS5 keyword search returns at least one chunk for each document."""
        conn = sqlite3.connect(str(FTS_PATH))
        cur = conn.cursor()

        results_summary = []
        for expected_doc, query in PROBES:
            # Tokenize and sanitize for FTS5
            tokens = re.findall(r"\w+", query)
            fts_query = " OR ".join(f'"{t}"' for t in tokens if len(t) > 2)
            cur.execute(
                "SELECT chunk_id, doc_id, section_id, citation, rank FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY rank LIMIT 5",
                (fts_query,),
            )
            rows = cur.fetchall()
            retrieved_docs = [r[1] for r in rows]

            self.assertIn(
                expected_doc,
                retrieved_docs,
                f"FTS5 failed to retrieve expected doc {expected_doc} for probe: '{query}'. Got: {retrieved_docs}",
            )
            top_hit = rows[0]
            results_summary.append((expected_doc, top_hit[0], top_hit[1], top_hit[3]))

        conn.close()
        print("\nFTS5 Probe Hits (Top 1):")
        for exp, chunk_id, doc_id, citation in results_summary:
            print(f"  Expected {exp} -> Found {doc_id} (chunk {chunk_id}, citation {citation})")

    def test_chroma_vector_probes(self):
        """Tests that Chroma vector search returns at least one chunk for each document."""
        results_summary = []
        for expected_doc, query in PROBES:
            q_emb = self.embed_model.encode([query], normalize_embeddings=True).tolist()
            res = self.collection.query(query_embeddings=q_emb, n_results=5)

            retrieved_docs = [m["doc_id"] for m in res["metadatas"][0]]
            self.assertIn(
                expected_doc,
                retrieved_docs,
                f"Chroma failed to retrieve expected doc {expected_doc} for probe: '{query}'. Got: {retrieved_docs}",
            )
            top_doc = res["metadatas"][0][0]["doc_id"]
            top_chunk = res["ids"][0][0]
            top_cit = res["metadatas"][0][0]["citation"]
            results_summary.append((expected_doc, top_chunk, top_doc, top_cit))

        print("\nChroma Vector Probe Hits (Top 1):")
        for exp, chunk_id, doc_id, citation in results_summary:
            print(f"  Expected {exp} -> Found {doc_id} (chunk {chunk_id}, citation {citation})")


if __name__ == "__main__":
    unittest.main()
