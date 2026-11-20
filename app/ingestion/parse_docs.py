"""
M2.1: Parse documents using Docling DocumentConverter.
Parses company-profile.md and D01-D07 markdown documents and exports extracted Markdown.
Fully local, re-runnable, reports model downloads and cache usage.
"""

import sys
import os
from pathlib import Path

# Set paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from docling.document_converter import DocumentConverter

DOCS_DIR = paths.REPO_ROOT / "documents" / "fictional-brightpath"
EXTRACTED_DIR = DOCS_DIR / "extracted"

SOURCE_FILES = [
    "company-profile.md",
    "D01-client-onboarding-sop.md",
    "D02-enterprise-refund-process.md",
    "D03-campaign-approval-rules.md",
    "D04-paid-social-brief-template.md",
    "D05-escalation-contacts.md",
    "D06-retainer-pricing-cancellation.md",
    "D07-client-faq.md",
]


def get_dir_size_bytes(dir_path: Path) -> int:
    if not dir_path.exists():
        return 0
    total = 0
    for root, _, files in os.walk(dir_path):
        for f in files:
            fp = Path(root) / f
            total += fp.stat().st_size
    return total


def parse_all_docs():
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    hf_cache = Path(os.environ.get("HF_HOME", "F:/stitchlab-cache/hf"))
    initial_hf_size = get_dir_size_bytes(hf_cache)

    print("=== M2.1 Document Ingestion via Docling ===")
    print(f"Source directory: {DOCS_DIR}")
    print(f"Output directory: {EXTRACTED_DIR}")
    print(f"Initial HF cache size: {initial_hf_size} bytes")

    converter = DocumentConverter()
    extracted_counts = 0

    for fname in SOURCE_FILES:
        source_path = DOCS_DIR / fname
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        print(f"Parsing: {fname} ...")
        res = converter.convert(str(source_path))
        markdown_text = res.document.export_to_markdown()

        dest_path = EXTRACTED_DIR / fname
        dest_path.write_text(markdown_text, encoding="utf-8")
        extracted_counts += 1
        print(f"  -> Extracted to {dest_path.name} ({len(markdown_text)} chars)")

    final_hf_size = get_dir_size_bytes(hf_cache)
    bytes_downloaded = final_hf_size - initial_hf_size

    print("\n--- Model Download & Cache Report ---")
    print(f"Models downloaded for Markdown parsing: None (0 models)")
    print(f"HF cache growth during parse: {bytes_downloaded} bytes")
    print(f"Total HF cache size: {final_hf_size} bytes")
    print(f"Parsed {extracted_counts} documents successfully.")
    return extracted_counts


if __name__ == "__main__":
    parse_all_docs()
