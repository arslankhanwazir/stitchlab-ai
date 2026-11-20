"""
M4.2: Citation Check and Normalization.
Parses citations from model answers, normalizes format variants,
verifies cited (doc, section) exists in retrieved passages,
and replaces unmatched/fake citations with an error note.
"""

import re
from typing import List, Dict, Any, Tuple, Set


# Regex to capture citations like:
# [D01, 3], [D03, §2], [D03, Section 2.2], [D05, Sec 1], [D02, 4.2]
# Also captures any [Dxx, ...] format for validation
CITATION_PATTERN = re.compile(
    r"\[\s*(D\d{2})\s*,\s*(?:§\s*|Section\s*|Sec\.?\s*)?(\d+(?:\.\d+)?)\s*\]",
    re.IGNORECASE,
)

# Catch-all for brackets mentioning doc ID to catch malformed citations
ANY_DOC_CITATION_PATTERN = re.compile(
    r"\[\s*(D\d{1,3})\s*[,:]?\s*([^\]]+)?\]",
    re.IGNORECASE,
)


def normalize_citation(doc_id: str, sec_raw: str) -> Tuple[str, str]:
    """
    Normalizes doc ID and section number.
    e.g. ('d03', 'Section 2.2') -> ('D03', '2')
    A cited paragraph number like 2.2 normalizes to section 2.
    """
    clean_doc = doc_id.strip().upper()
    sec_clean = sec_raw.strip() if sec_raw else "0"

    # Strip prefixes like §, Section, Sec.
    sec_clean = re.sub(r"^(?:§|Section|Sec\.?)\s*", "", sec_clean, flags=re.IGNORECASE).strip()

    # Extract major section number (e.g. 2 from 2.2)
    m = re.match(r"^(\d+)(?:\.\d+)?", sec_clean)
    if m:
        normalized_sec = m.group(1)
    else:
        normalized_sec = sec_clean

    return clean_doc, normalized_sec


def get_valid_passage_keys(passages: List[Dict[str, Any]]) -> Set[Tuple[str, str]]:
    """Builds a set of (doc_id, section_id) from the retrieved passages."""
    valid_keys = set()
    for p in passages:
        doc_id = p.get("doc_id", "").strip().upper()
        sec_id = str(p.get("section_id", "")).strip()
        if doc_id:
            # Add exact section
            valid_keys.add((doc_id, sec_id))
            # Also normalize if sec_id contains dots
            m = re.match(r"^(\d+)(?:\.\d+)?", sec_id)
            if m:
                valid_keys.add((doc_id, m.group(1)))
    return valid_keys


def verify_and_filter_citations(
    answer: str,
    retrieved_passages: List[Dict[str, Any]],
) -> Tuple[str, List[Dict[str, Any]], bool]:
    """
    Parses citations from answer, verifies against retrieved passages.
    Replaces unmatched citations with: [INVALID CITATION: <original>]

    Returns:
        (sanitized_answer, citation_records, all_valid)
    """
    valid_keys = get_valid_passage_keys(retrieved_passages)
    citation_records = []
    all_valid = True

    def replace_citation(match: re.Match) -> str:
        nonlocal all_valid
        full_cit = match.group(0)
        doc_raw = match.group(1)
        sec_raw = match.group(2) if match.lastindex >= 2 else ""

        norm_doc, norm_sec = normalize_citation(doc_raw, sec_raw)
        is_valid = (norm_doc, norm_sec) in valid_keys

        record = {
            "raw": full_cit,
            "doc_id": norm_doc,
            "section_id": norm_sec,
            "is_valid": is_valid,
        }
        citation_records.append(record)

        if is_valid:
            return full_cit
        else:
            all_valid = False
            return f"[INVALID CITATION: {full_cit.strip('[]')}]"

    # First pass: standard citation pattern
    sanitized_answer = CITATION_PATTERN.sub(replace_citation, answer)

    return sanitized_answer, citation_records, all_valid
