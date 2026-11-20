"""
M4.3: Pure deterministic conflict detection across retrieved passages.
No LLM is used.

Detects exactly two conflict types across DIFFERENT documents:
- Type 1: Two different numbers/amounts (with the same unit or currency) for the same item.
- Type 2: Opposite polarity/instruction (must/must not, required/not required, allowed/not allowed, can/cannot).

Output format:
"Conflicting instructions: [DocID_A, Sec_A] says X; [DocID_B, Sec_B] says Y."
"""

import re
import difflib
from typing import List, Dict, Any, Optional, Tuple, Set


# Currency amount pattern: $15,000 or $10,000
CURRENCY_PATTERN = re.compile(r"(\$[\d,]+(?:\.\d+)?)")

# Duration / time period pattern: 5 working days, 30 calendar days
DURATION_PATTERN = re.compile(
    r"(\b\d+\s+(?:working|calendar|business)\s+(?:days?|hours?|weeks?|months?)\b)",
    re.IGNORECASE,
)

# Polarity pairs for Type 2
POLARITY_PAIRS = [
    (r"\bmust\s+not\b", r"\bmust\b"),
    (r"\bnot\s+required\b", r"\brequired\b"),
    (r"\bnot\s+allowed\b", r"\ballowed\b"),
    (r"\bcannot\b", r"\bcan\b"),
    (r"\bprohibited\b", r"\bpermitted\b"),
]

# Stopwords to exclude when measuring lexical overlap
STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "in", "on", "at", "to", "for", "with",
    "by", "is", "are", "was", "were", "be", "been", "this", "that", "these",
    "those", "it", "its", "each", "every", "all", "see", "per"
}


def clean_sentence(text: str) -> str:
    """Cleans markdown list/heading markers from a sentence."""
    text = re.sub(r"^\s*(?:#+|\d+\.\d*|\*|-)\s*", "", text)
    return text.strip()


def extract_sentences(passage_text: str) -> List[str]:
    """Splits passage into clean individual sentences."""
    raw_lines = passage_text.split("\n")
    sentences = []
    for line in raw_lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("|"):
            continue
        # Split on sentence terminals
        parts = re.split(r"(?<=[.!?])\s+", line)
        for p in parts:
            p_clean = clean_sentence(p)
            if len(p_clean) > 10:
                sentences.append(p_clean)
    return sentences


def get_token_stems(sentence: str, remove_patterns: List[re.Pattern]) -> Set[str]:
    """Extracts non-stopword token stems after removing target patterns."""
    text = sentence.lower()
    for pat in remove_patterns:
        text = pat.sub(" ", text)

    words = re.findall(r"\b[a-z]{3,}\b", text)
    stems = set()
    for w in words:
        if w in STOPWORDS:
            continue
        # Simple suffix stripping for rough stemming
        if w.endswith("ing") and len(w) > 5:
            w = w[:-3]
        elif w.endswith("s") and len(w) > 4:
            w = w[:-1]
        elif w.endswith("ed") and len(w) > 4:
            w = w[:-2]
        stems.add(w)
    return stems


def format_conflict_statement(cit_a: str, sent_a: str, cit_b: str, sent_b: str) -> str:
    """Formats conflict string without doubled punctuation (e.g. no '.;' or '..')."""
    clean_a = sent_a.rstrip(".!?;, ")
    clean_b = sent_b.rstrip(".!?;, ")
    return f"Conflicting instructions: {cit_a} says {clean_a}; {cit_b} says {clean_b}."


def compute_lexical_similarity(stems_a: Set[str], stems_b: Set[str]) -> float:
    """Computes Jaccard similarity between two sets of token stems."""
    if not stems_a or not stems_b:
        return 0.0
    intersection = stems_a.intersection(stems_b)
    union = stems_a.union(stems_b)
    return len(intersection) / len(union)


def check_conflicts(passages: List[Dict[str, Any]]) -> Optional[str]:
    """
    Checks for Type 1 and Type 2 conflicts across passages of DIFFERENT documents.
    Returns:
        Formatted conflict string or None if no conflict found.
    """
    if len(passages) < 2:
        return None

    # De-duplicate passages by doc_id + section_id
    seen_chunks = set()
    unique_passages = []
    for p in passages:
        key = (p.get("doc_id"), str(p.get("section_id")))
        if key not in seen_chunks:
            seen_chunks.add(key)
            unique_passages.append(p)

    # Extract sentences per passage
    passage_sentences = []
    for p in unique_passages:
        doc_id = p.get("doc_id", "")
        sec_id = str(p.get("section_id", ""))
        cit = p.get("citation", f"[{doc_id}, {sec_id}]")
        sents = extract_sentences(p.get("text", ""))
        for s in sents:
            passage_sentences.append({
                "doc_id": doc_id,
                "section_id": sec_id,
                "citation": cit,
                "sentence": s,
            })

    # Compare pairs from DIFFERENT documents
    n = len(passage_sentences)
    for i in range(n):
        for j in range(i + 1, n):
            s_a = passage_sentences[i]
            s_b = passage_sentences[j]

            # Rule: MUST be from different documents
            if s_a["doc_id"] == s_b["doc_id"]:
                continue

            text_a = s_a["sentence"]
            text_b = s_b["sentence"]

            # =========================================================
            # Type 1: Different numbers/amounts for the same item
            # =========================================================
            # Case 1A: Currency amounts ($15,000 vs $10,000)
            currencies_a = CURRENCY_PATTERN.findall(text_a)
            currencies_b = CURRENCY_PATTERN.findall(text_b)
            if currencies_a and currencies_b:
                val_a = currencies_a[0]
                val_b = currencies_b[0]
                if val_a != val_b:
                    stems_a = get_token_stems(text_a, [CURRENCY_PATTERN])
                    stems_b = get_token_stems(text_b, [CURRENCY_PATTERN])
                    sim = compute_lexical_similarity(stems_a, stems_b)
                    # High overlap on non-number words
                    if sim >= 0.25:
                        return format_conflict_statement(
                            s_a['citation'], text_a, s_b['citation'], text_b
                        )

            # Case 1B: Duration with same units (e.g. 5 working days vs 10 working days)
            durations_a = DURATION_PATTERN.findall(text_a)
            durations_b = DURATION_PATTERN.findall(text_b)
            if durations_a and durations_b:
                dur_a = durations_a[0].lower()
                dur_b = durations_b[0].lower()
                if dur_a != dur_b:
                    stems_a = get_token_stems(text_a, [DURATION_PATTERN])
                    stems_b = get_token_stems(text_b, [DURATION_PATTERN])
                    sim = compute_lexical_similarity(stems_a, stems_b)
                    if sim >= 0.50:  # Require high similarity to ensure it's the exact same item
                        return format_conflict_statement(
                            s_a['citation'], text_a, s_b['citation'], text_b
                        )

            # =========================================================
            # Type 2: Opposite polarity (must vs must not, etc.)
            # =========================================================
            for neg_pat, pos_pat in POLARITY_PAIRS:
                neg_re = re.compile(neg_pat, re.IGNORECASE)
                pos_re = re.compile(pos_pat, re.IGNORECASE)

                is_a_neg = bool(neg_re.search(text_a))
                is_b_neg = bool(neg_re.search(text_b))
                is_a_pos = bool(pos_re.search(text_a)) and not is_a_neg
                is_b_pos = bool(pos_re.search(text_b)) and not is_b_neg

                if (is_a_neg and is_b_pos) or (is_a_pos and is_b_neg):
                    stems_a = get_token_stems(text_a, [neg_re, pos_re])
                    stems_b = get_token_stems(text_b, [neg_re, pos_re])
                    sim = compute_lexical_similarity(stems_a, stems_b)
                    if sim >= 0.50:
                        return format_conflict_statement(
                            s_a['citation'], text_a, s_b['citation'], text_b
                        )

    return None
