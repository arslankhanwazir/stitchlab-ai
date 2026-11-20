"""
M3.1: Hybrid search combining SQLite FTS5 (keyword) and Chroma (vector).
- Retrieves up to 10 candidates from FTS5 and 10 from Chroma.
- Merges using Reciprocal Rank Fusion (k=60).
- Deduplicates by chunk_id.
- Sanitizes FTS5 query to prevent punctuation syntax errors.
"""

import sys
import os
import re
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

# Telemetry off, offline models
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

from sentence_transformers import SentenceTransformer
import chromadb
from app.ingestion.build_index import (
    CHROMA_DIR,
    FTS_PATH,
    COLLECTION_NAME,
    MODEL_NAME,
)

_embed_model: Optional[SentenceTransformer] = None
_chroma_collection = None


def get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(MODEL_NAME)
    return _embed_model


def get_chroma_collection():
    global _chroma_collection
    if _chroma_collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _chroma_collection = client.get_collection(name=COLLECTION_NAME, embedding_function=None)
    return _chroma_collection


def sanitize_fts5_query(query: str) -> str:
    """Extracts alphanumeric words and formats as OR-separated quoted tokens."""
    # Split on whitespace/punctuation into alphanumeric tokens
    tokens = re.findall(r"[A-Za-z0-9]+", query)
    # Filter short stopwords / single letters except meaningful numbers
    valid_tokens = [t for t in tokens if len(t) > 1 or t.isdigit()]
    if not valid_tokens:
        return '""'
    return " OR ".join(f'"{t}"' for t in valid_tokens)


def fts5_search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Runs keyword search on SQLite FTS5 index."""
    if not FTS_PATH.exists():
        raise FileNotFoundError(f"FTS index not found at {FTS_PATH}. Run build_index.py first.")

    sanitized = sanitize_fts5_query(query)
    if sanitized == '""':
        return []

    conn = sqlite3.connect(str(FTS_PATH))
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT chunk_id, doc_id, section_id, section_title, version, last_reviewed, citation, text, rank
            FROM chunks_fts
            WHERE chunks_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (sanitized, limit),
        )
        rows = cur.fetchall()
    except sqlite3.OperationalError as e:
        print(f"FTS5 query error on '{sanitized}': {e}")
        rows = []
    finally:
        conn.close()

    results = []
    for rank_idx, row in enumerate(rows, start=1):
        results.append({
            "chunk_id": row[0],
            "doc_id": row[1],
            "section_id": row[2],
            "section_title": row[3],
            "version": row[4],
            "last_reviewed": row[5],
            "citation": row[6],
            "text": row[7],
            "bm25_score": row[8],
            "fts_rank": rank_idx,
        })
    return results


def vector_search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Runs vector search on Chroma persistent vector store."""
    if not CHROMA_DIR.exists():
        raise FileNotFoundError(f"Chroma index not found at {CHROMA_DIR}. Run build_index.py first.")

    embedder = get_embed_model()
    q_emb = embedder.encode([query], normalize_embeddings=True).tolist()

    collection = get_chroma_collection()
    res = collection.query(query_embeddings=q_emb, n_results=limit)

    results = []
    if res and res["ids"] and len(res["ids"][0]) > 0:
        ids = res["ids"][0]
        docs = res["documents"][0]
        metas = res["metadatas"][0]
        distances = res["distances"][0] if "distances" in res and res["distances"] else [0.0] * len(ids)

        for rank_idx, (cid, doc, meta, dist) in enumerate(zip(ids, docs, metas, distances), start=1):
            results.append({
                "chunk_id": cid,
                "doc_id": meta.get("doc_id", ""),
                "section_id": meta.get("section_id", ""),
                "section_title": meta.get("section_title", ""),
                "version": meta.get("version", ""),
                "last_reviewed": meta.get("last_reviewed", ""),
                "citation": meta.get("citation", f"[{meta.get('doc_id')}, {meta.get('section_id')}]"),
                "text": doc,
                "vector_distance": dist,
                "vector_rank": rank_idx,
            })
    return results


def reciprocal_rank_fusion(
    fts_results: List[Dict[str, Any]],
    vector_results: List[Dict[str, Any]],
    k: int = 60,
    top_n: int = 10,
) -> List[Dict[str, Any]]:
    """Merges FTS and vector results using Reciprocal Rank Fusion (k=60)."""
    scores: Dict[str, float] = {}
    chunk_map: Dict[str, Dict[str, Any]] = {}

    for item in fts_results:
        cid = item["chunk_id"]
        rank = item["fts_rank"]
        scores[cid] = scores.get(cid, 0.0) + (1.0 / (k + rank))
        if cid not in chunk_map:
            chunk_map[cid] = dict(item)
        else:
            chunk_map[cid]["fts_rank"] = rank
            chunk_map[cid]["bm25_score"] = item["bm25_score"]

    for item in vector_results:
        cid = item["chunk_id"]
        rank = item["vector_rank"]
        scores[cid] = scores.get(cid, 0.0) + (1.0 / (k + rank))
        if cid not in chunk_map:
            chunk_map[cid] = dict(item)
        else:
            chunk_map[cid]["vector_rank"] = rank
            chunk_map[cid]["vector_distance"] = item["vector_distance"]

    # Sort descending by RRF score
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

    merged: List[Dict[str, Any]] = []
    for rank_idx, cid in enumerate(sorted_ids[:top_n], start=1):
        entry = chunk_map[cid]
        entry["rrf_score"] = round(scores[cid], 6)
        entry["hybrid_rank"] = rank_idx
        # Default ranks if absent in one of the lists
        if "fts_rank" not in entry:
            entry["fts_rank"] = None
        if "vector_rank" not in entry:
            entry["vector_rank"] = None
        merged.append(entry)

    return merged


def hybrid_search(query: str, top_candidates: int = 10, k: int = 60) -> List[Dict[str, Any]]:
    """Executes full hybrid search: FTS5 + Vector -> RRF merge."""
    fts_hits = fts5_search(query, limit=top_candidates)
    vector_hits = vector_search(query, limit=top_candidates)
    return reciprocal_rank_fusion(fts_hits, vector_hits, k=k, top_n=top_candidates)


if __name__ == "__main__":
    test_q = "Who signs off creative before a campaign goes live?"
    print(f"Test Query: {test_q}")
    hits = hybrid_search(test_q, top_candidates=5)
    for h in hits:
        print(f"Rank {h['hybrid_rank']}: {h['chunk_id']} ({h['citation']}) | RRF: {h['rrf_score']} | FTS: {h['fts_rank']} | Vector: {h['vector_rank']}")
