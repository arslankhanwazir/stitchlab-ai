"""
M6B.2: Reversible Data Masking for PII and Sensitive Attributes.
Masks:
- Email addresses (regex)
- Phone numbers (regex)
- Exact-match personnel names compiled from D01..D07 tables and company profile
Reversible: unmask(masked_text, mapping) restores original text exactly before display.
"""

import re
from typing import Tuple, Dict, List

# Compiled known personnel names from D01..D07 and profile
KNOWN_NAMES: List[str] = [
    "Sam Whitfield",
    "Tom Reyes",
    "Daniel Okafor",
    "Priya Shah",
    "Marcus Vance",
    "Elena Rostova",
    "David Chen",
    "Aisha Patel",
]

# Regex patterns
EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

# International and US phone formats (e.g. +1 555 0177, +1 555 0142, (555) 0177)
PHONE_PATTERN = re.compile(
    r"(?:\+\d{1,3}[-.\s]+)?(?:\(?\d{3}\)?[-.\s]+)?\d{3,4}[-.\s]+\d{4}\b"
)


def mask_data(text: str) -> Tuple[str, Dict[str, str]]:
    """
    Replaces PII (emails, phones, known personnel names) with reversible tokens.
    Returns:
        (masked_text, mapping_dict)
    """
    mapping: Dict[str, str] = {}
    counter = {
        "EMAIL": 0,
        "PHONE": 0,
        "NAME": 0,
    }

    # 1. Mask exact names first (to avoid partial overlaps)
    masked_text = text
    for name in KNOWN_NAMES:
        if name in masked_text:
            counter["NAME"] += 1
            token = f"[PERSON_NAME_{counter['NAME']}]"
            mapping[token] = name
            masked_text = masked_text.replace(name, token)

    # 2. Mask emails
    def email_repl(match):
        val = match.group(0)
        counter["EMAIL"] += 1
        token = f"[EMAIL_ADDR_{counter['EMAIL']}]"
        mapping[token] = val
        return token

    masked_text = EMAIL_PATTERN.sub(email_repl, masked_text)

    # 3. Mask phones
    def phone_repl(match):
        val = match.group(0)
        counter["PHONE"] += 1
        token = f"[PHONE_NUM_{counter['PHONE']}]"
        mapping[token] = val
        return token

    masked_text = PHONE_PATTERN.sub(phone_repl, masked_text)

    return masked_text, mapping


def unmask_data(masked_text: str, mapping: Dict[str, str]) -> str:
    """Restores masked tokens back to their original values."""
    unmasked = masked_text
    for token, original in mapping.items():
        unmasked = unmasked.replace(token, original)
    return unmasked
