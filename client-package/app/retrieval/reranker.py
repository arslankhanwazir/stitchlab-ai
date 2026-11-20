"""
M3.2: Local Cross-Encoder Reranker.
Reranks hybrid search candidates using cross-encoder/ms-marco-MiniLM-L-6-v2.
Completely offline, local, fast on CPU.
"""

import sys
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Telemetry off, offline models
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from sentence_transformers import CrossEncoder

RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_cross_encoder: Optional[CrossEncoder] = None


def get_reranker() -> CrossEncoder:
    global _cross_encoder
    if _cross_encoder is None:
        _cross_encoder = CrossEncoder(RERANKER_MODEL_NAME)
    return _cross_encoder


def rerank(query: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Reranks candidates for a given query using the cross-encoder model.
    Adds 'rerank_score' and 'rerank_rank' to each candidate.
    Returns sorted candidates descending by rerank_score.
    """
    if not candidates:
        return []

    model = get_reranker()
    pairs = [(query, c["text"]) for c in candidates]

    t0 = time.time()
    scores = model.predict(pairs, show_progress_bar=False)
    elapsed = time.time() - t0

    scored_candidates = []
    for c, s in zip(candidates, scores):
        item = dict(c)
        item["rerank_score"] = float(round(float(s), 4))
        scored_candidates.append(item)

    scored_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)

    for idx, item in enumerate(scored_candidates, start=1):
        item["rerank_rank"] = idx

    return scored_candidates


if __name__ == "__main__":
    from app.retrieval.hybrid import hybrid_search

    q = "Who signs off creative before a campaign goes live?"
    raw_hits = hybrid_search(q, top_candidates=5)
    reranked = rerank(q, raw_hits)

    print(f"Query: {q}")
    print("\n--- Before Reranking (Hybrid RRF) ---")
    for h in raw_hits:
        print(f"  Rank {h['hybrid_rank']}: {h['chunk_id']} ({h['citation']}) | RRF: {h['rrf_score']}")

    print("\n--- After Reranking (Cross-Encoder) ---")
    for h in reranked:
        print(f"  Rank {h['rerank_rank']}: {h['chunk_id']} ({h['citation']}) | Score: {h['rerank_score']}")
