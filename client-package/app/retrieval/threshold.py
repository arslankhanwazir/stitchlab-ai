"""
M3.3: Relevance Threshold Filtering.
Applies a minimum relevance score cutoff to reranked candidate chunks.
- If top candidate score < MIN_RELEVANCE_SCORE, declares query unanswerable ("Not found in your documents").
- Filters out passages below threshold, returning only qualifying evidence passages.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

# Chosen threshold based on empirical calibration:
# Q01-Q08 lowest top score: 3.7900 (Q02)
# Q09 (unanswerable) top score: -3.1991
# Q10 (conflict) relevant chunks: D04_2 (3.8807), D03_2 (2.7661)
# Threshold 0.0 provides a safety margin of ~3.8 to 7.0 points.
MIN_RELEVANCE_SCORE: float = 0.0
NOT_FOUND_MESSAGE: str = "Not found in your documents."


def apply_threshold(
    reranked_candidates: List[Dict[str, Any]],
    threshold: float = MIN_RELEVANCE_SCORE,
) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Evaluates top candidate score against threshold.
    Returns:
        (qualifying_passages, is_found)
    If no passages qualify or top passage is below threshold, returns ([], False).
    """
    if not reranked_candidates:
        return [], False

    top_score = reranked_candidates[0].get("rerank_score", -999.0)
    if top_score < threshold:
        return [], False

    # Keep all candidates meeting or exceeding the minimum score
    qualifying = [c for c in reranked_candidates if c.get("rerank_score", -999.0) >= threshold]
    if not qualifying:
        return [], False

    return qualifying, True


def retrieve_and_threshold(
    query: str,
    top_candidates: int = 10,
    threshold: float = MIN_RELEVANCE_SCORE,
) -> Tuple[List[Dict[str, Any]], bool]:
    """Full retrieval pipeline through thresholding: hybrid -> rerank -> threshold."""
    from app.retrieval.hybrid import hybrid_search
    from app.retrieval.reranker import rerank

    hits = hybrid_search(query, top_candidates=top_candidates)
    reranked = rerank(query, hits)
    return apply_threshold(reranked, threshold=threshold)
