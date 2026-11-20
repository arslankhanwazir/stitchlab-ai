"""
Pre-download Models for StitchLab AI.
Pre-downloads the required models during initial setup:
1. sentence-transformers/all-MiniLM-L6-v2 (Embedding model for Chroma vector search)
2. cross-encoder/ms-marco-MiniLM-L-6-v2 (Cross-encoder reranker model)

Once executed during setup, models reside in the local cache (HF_HOME) and all subsequent
app operations run completely offline with HF_HUB_OFFLINE=1 and TRANSFORMERS_OFFLINE=1.
"""

import os
import sys
from pathlib import Path

# Paths setup
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def pre_download_models():
    """Downloads both approved models into local HuggingFace cache or verifies existing cache."""
    from sentence_transformers import SentenceTransformer, CrossEncoder

    print(f"Checking/caching embedding model: {EMBEDDING_MODEL_NAME}...")
    SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("Embedding model cached successfully.")

    print(f"Checking/caching reranker model: {RERANKER_MODEL_NAME}...")
    CrossEncoder(RERANKER_MODEL_NAME)
    print("Reranker model cached successfully.")
    print("All models verified in local cache.")


if __name__ == "__main__":
    pre_download_models()
