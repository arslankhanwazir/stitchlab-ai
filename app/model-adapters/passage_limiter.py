"""
M6B.1: Passage Limiting and Hard Cap Enforcement.
Enforces a hard cap of <= 5 passages (default 4) sent to any LLM.
Prevents context bloating and reduces exposure surface.
"""

from typing import List, Dict, Any

DEFAULT_PASSAGE_LIMIT = 4
HARD_PASSAGE_CAP = 5


def enforce_passage_limit(
    passages: List[Dict[str, Any]],
    limit: int = DEFAULT_PASSAGE_LIMIT,
    hard_cap: int = HARD_PASSAGE_CAP,
) -> List[Dict[str, Any]]:
    """
    Applies the configured passage limit up to the strict hard cap.
    If requested limit > hard_cap, it is clamped to hard_cap.
    """
    effective_limit = min(limit, hard_cap)
    if effective_limit < 1:
        effective_limit = 1
    return passages[:effective_limit]
