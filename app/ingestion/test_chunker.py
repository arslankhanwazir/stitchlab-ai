"""
M2.2 Done-check test for chunker.
Uses stdlib unittest.
Asserts every chunk has:
- doc_id
- section_title
- page key (page null is allowed and recorded)
- version date (last_reviewed)
- valid citation [DocID, Section]
"""

import sys
import unittest
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths
from app.ingestion.chunker import get_all_chunks, CHUNKING_NOTE


class TestChunker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chunks = get_all_chunks()

    def test_chunk_count(self):
        self.assertEqual(len(self.chunks), 29, "Expected exactly 29 chunks across D01-D07")

    def test_metadata_fields_present_in_every_chunk(self):
        required_keys = {"chunk_id", "doc_id", "section_id", "section_title", "page", "version", "last_reviewed", "text", "citation"}
        for chunk in self.chunks:
            with self.subTest(chunk_id=chunk.get("chunk_id")):
                # Check all keys exist
                for k in required_keys:
                    self.assertIn(k, chunk, f"Chunk {chunk.get('chunk_id')} missing key '{k}'")

                # doc_id must be D01..D07
                self.assertRegex(chunk["doc_id"], r"^D0[1-7]$")

                # section_id must be non-empty numeric string
                self.assertTrue(chunk["section_id"].isdigit())

                # section_title must be non-empty string
                self.assertIsInstance(chunk["section_title"], str)
                self.assertTrue(len(chunk["section_title"].strip()) > 0)

                # page key must exist; for markdown source page must be None (null)
                self.assertIsNone(chunk["page"], "Markdown source requires page=None")

                # version date (last_reviewed) must be YYYY-MM-DD
                self.assertRegex(chunk["last_reviewed"], r"^\d{4}-\d{2}-\d{2}$")

                # version must be valid version string (e.g. '1.4', '2.1')
                self.assertRegex(chunk["version"], r"^\d+\.\d+$")

                # text must be non-empty
                self.assertTrue(len(chunk["text"].strip()) > 20)

                # citation must match [DocID, Section]
                self.assertEqual(chunk["citation"], f"[{chunk['doc_id']}, {chunk['section_id']}]")

    def test_chunking_note_exists(self):
        self.assertTrue(CHUNKING_NOTE.exists(), "chunking-note.md must exist")
        content = CHUNKING_NOTE.read_text(encoding="utf-8")
        self.assertIn("Brightpath Media (demo) Chunking Note", content)
        self.assertIn("D01_3", content)
        self.assertIn("D03_2", content)


if __name__ == "__main__":
    unittest.main()
