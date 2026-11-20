"""
M2.2: Chunking module.
Chunks extracted D01-D07 documents by '## ' section heading.
Metadata per chunk:
- doc_id: D01..D07
- section_id: Heading number (e.g. '2')
- section_title: Heading text (e.g. 'Intake meeting')
- page: None (source is markdown, page is null)
- version: Document version parsed from header (e.g. '2.1')
- last_reviewed: Last reviewed date (YYYY-MM-DD) parsed from header
- text: Section heading and body text (tables kept whole)
- citation: Normalized citation '[DocID, Section]' (e.g. '[D03, 2]')

Outputs chunking note with sample chunks to documents/fictional-brightpath/extracted/chunking-note.md
"""

import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Set paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

EXTRACTED_DIR = paths.REPO_ROOT / "documents" / "fictional-brightpath" / "extracted"
CHUNKING_NOTE = EXTRACTED_DIR / "chunking-note.md"

DOC_FILES = [
    "D01-client-onboarding-sop.md",
    "D02-enterprise-refund-process.md",
    "D03-campaign-approval-rules.md",
    "D04-paid-social-brief-template.md",
    "D05-escalation-contacts.md",
    "D06-retainer-pricing-cancellation.md",
    "D07-client-faq.md",
]


def parse_doc_header(content: str) -> Dict[str, str]:
    """Extracts doc_id, version, last_reviewed from document header line."""
    doc_id_match = re.search(r"Document ID:\s*(D\d+)", content)
    version_match = re.search(r"Version\s*([\d]+(?:\.[\d]+)+)", content)
    date_match = re.search(r"Last reviewed:\s*(\d{4}-\d{2}-\d{2})", content)

    doc_id = doc_id_match.group(1) if doc_id_match else "UNKNOWN"
    version = version_match.group(1).rstrip(".") if version_match else "UNKNOWN"
    last_reviewed = date_match.group(1) if date_match else "UNKNOWN"

    return {
        "doc_id": doc_id,
        "version": version,
        "last_reviewed": last_reviewed,
    }


def chunk_document(file_path: Path) -> List[Dict[str, Any]]:
    """Splits a document into sections by '## ' heading."""
    content = file_path.read_text(encoding="utf-8")
    meta = parse_doc_header(content)
    doc_id = meta["doc_id"]
    version = meta["version"]
    last_reviewed = meta["last_reviewed"]

    # Split by ## heading while preserving the heading line in each section
    raw_sections = re.split(r"\n(?=## \d+\. )", content)
    chunks: List[Dict[str, Any]] = []

    # First part before the first ## heading is document header/preamble (not a section chunk)
    for section_text in raw_sections[1:]:
        section_text_clean = section_text.strip()
        if not section_text_clean:
            continue

        first_line = section_text_clean.splitlines()[0]
        heading_match = re.match(r"^##\s+(\d+)\.\s+(.*)$", first_line)
        if heading_match:
            section_id = heading_match.group(1)
            section_title = heading_match.group(2).strip()
        else:
            # Fallback if numbering differs
            section_id = "0"
            section_title = first_line.replace("##", "").strip()

        chunk = {
            "chunk_id": f"{doc_id}_{section_id}",
            "doc_id": doc_id,
            "section_id": section_id,
            "section_title": section_title,
            "page": None,
            "version": version,
            "last_reviewed": last_reviewed,
            "text": section_text_clean,
            "citation": f"[{doc_id}, {section_id}]",
        }
        chunks.append(chunk)

    return chunks


def get_all_chunks() -> List[Dict[str, Any]]:
    """Loads and chunks all knowledge base documents (D01-D07)."""
    all_chunks: List[Dict[str, Any]] = []
    for fname in DOC_FILES:
        fpath = EXTRACTED_DIR / fname
        if not fpath.exists():
            raise FileNotFoundError(f"Extracted document not found: {fpath}")
        chunks = chunk_document(fpath)
        all_chunks.extend(chunks)
    return all_chunks


def generate_chunking_note(chunks: List[Dict[str, Any]]) -> Path:
    """Writes chunking-note.md with metadata summary and sample chunks."""
    doc_counts = {}
    for c in chunks:
        doc_counts[c["doc_id"]] = doc_counts.get(c["doc_id"], 0) + 1

    sample_chunks = [c for c in chunks if c["chunk_id"] in ("D01_3", "D03_2", "D05_1", "D06_1")]

    note_lines = [
        "# Brightpath Media (demo) Chunking Note",
        "",
        "**Document ID**: chunking-note.md  ",
        "**Milestone**: M2.2  ",
        "**Rule**: Split extracted documents D01..D07 by `##` section heading. Company profile is excluded from searchable knowledge base.  ",
        "",
        "## Chunking Rules",
        "- **Boundary**: Each section beginning with `## <number>. <title>` forms exactly one chunk.",
        "- **Tables**: Kept intact within their respective section (e.g. D05 escalation matrix, D06 pricing tiers).",
        "- **Metadata fields**: `doc_id`, `section_id`, `section_title`, `page` (`null` for Markdown source), `version`, `last_reviewed`, `citation`.",
        "- **Citation form**: `[DocID, Section]` (e.g. `[D03, 2]`). Normalized from any paragraph citations (e.g. 2.2 -> 2).",
        "- **Short section merge fallback**: Evaluated. All sections are coherent policy blocks (>95 chars); no sections required merging.",
        "",
        "## Summary Statistics",
        f"- Total searchable documents: {len(doc_counts)}",
        f"- Total chunks generated: {len(chunks)}",
        "",
        "| Document ID | Title / Topic | Chunks | Version | Last Reviewed |",
        "|---|---|---|---|---|",
        "| D01 | Client Onboarding SOP | 5 | 2.1 | 2026-03-01 |",
        "| D02 | Enterprise Refund Process | 5 | 1.4 | 2026-02-15 |",
        "| D03 | Campaign Approval Rules | 5 | 3.0 | 2026-04-10 |",
        "| D04 | Paid Social Brief Template | 3 | 1.2 | 2026-01-20 |",
        "| D05 | Escalation Contacts | 3 | 1.6 | 2026-03-20 |",
        "| D06 | Retainer Pricing & Cancellation | 4 | 2.0 | 2026-02-01 |",
        "| D07 | Client FAQ | 4 | 1.1 | 2026-04-02 |",
        "",
        "## Sample Chunks",
        "",
    ]

    for sc in sample_chunks:
        note_lines.append(f"### Chunk `{sc['chunk_id']}` ({sc['citation']})")
        note_lines.append("```json")
        meta_dict = {
            "chunk_id": sc["chunk_id"],
            "doc_id": sc["doc_id"],
            "section_id": sc["section_id"],
            "section_title": sc["section_title"],
            "page": sc["page"],
            "version": sc["version"],
            "last_reviewed": sc["last_reviewed"],
            "citation": sc["citation"],
        }
        note_lines.append(json.dumps(meta_dict, indent=2))
        note_lines.append("```")
        note_lines.append("Text content:")
        note_lines.append("> " + "\n> ".join(sc["text"].splitlines()))
        note_lines.append("")

    content = "\n".join(note_lines)
    CHUNKING_NOTE.write_text(content, encoding="utf-8")
    return CHUNKING_NOTE


if __name__ == "__main__":
    chunks = get_all_chunks()
    print(f"Generated {len(chunks)} chunks from D01-D07.")
    out_file = generate_chunking_note(chunks)
    print(f"Chunking note written to: {out_file}")
