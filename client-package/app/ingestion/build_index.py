"""
M2.3: Build local indexes (Chroma vector index + SQLite FTS5 keyword index).
- Checks SQLite FTS5 support.
- Encodes all chunks with sentence-transformers/all-MiniLM-L6-v2 (offline, local).
- Stores vectors in Chroma (local-index/chroma/) with embedding_function=None.
- Builds keyword index in SQLite FTS5 (local-index/fts.sqlite).
- Re-runnable rebuild script. Reports index build time and sizes.
"""

import sys
import os
import time
import sqlite3
import shutil
from pathlib import Path
from typing import Dict, Any

# Ensure telemetry is OFF
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Set paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths
from app.ingestion.chunker import get_all_chunks

LOCAL_INDEX_DIR = paths.REPO_ROOT / "local-index"
CHROMA_DIR = LOCAL_INDEX_DIR / "chroma"
FTS_PATH = LOCAL_INDEX_DIR / "fts.sqlite"
COLLECTION_NAME = "brightpath_chunks"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def check_fts5_support() -> bool:
    """Verifies that the Python sqlite3 build supports FTS5."""
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE VIRTUAL TABLE _test_fts5 USING fts5(content);")
        con.execute("INSERT INTO _test_fts5 VALUES ('test');")
        res = con.execute("SELECT * FROM _test_fts5 WHERE _test_fts5 MATCH 'test';").fetchall()
        return len(res) == 1
    except Exception as e:
        print(f"FTS5 check failed: {e}")
        return False
    finally:
        con.close()


def get_dir_size_bytes(dir_path: Path) -> int:
    """Calculates total size of a directory in bytes."""
    if not dir_path.exists():
        return 0
    total = 0
    for root, _, files in os.walk(dir_path):
        for f in files:
            fp = Path(root) / f
            total += fp.stat().st_size
    return total


def build_indexes() -> Dict[str, Any]:
    print("=== M2.3 Local Index Construction ===")
    
    # 1. SQLite FTS5 check
    fts5_ok = check_fts5_support()
    print(f"SQLite FTS5 support: {'SUPPORTED' if fts5_ok else 'UNSUPPORTED'}")
    if not fts5_ok:
        raise RuntimeError("SQLite FTS5 is not supported on this Python installation.")

    LOCAL_INDEX_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Load chunks
    chunks = get_all_chunks()
    print(f"Loaded {len(chunks)} chunks from D01-D07.")

    start_time = time.time()

    # 3. Load embedding model locally
    print(f"Loading embedding model '{MODEL_NAME}'...")
    from sentence_transformers import SentenceTransformer
    embed_model = SentenceTransformer(MODEL_NAME)

    texts = [c["text"] for c in chunks]
    print(f"Computing embeddings for {len(texts)} chunks...")
    t_embed_start = time.time()
    embeddings = embed_model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    t_embed_elapsed = time.time() - t_embed_start
    print(f"Embeddings computed in {t_embed_elapsed:.2f} s (shape: {embeddings.shape}).")

    # 4. Build Chroma persistent index
    import chromadb
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Building Chroma vector store at: {CHROMA_DIR}")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=None)

    ids = [c["chunk_id"] for c in chunks]
    metadatas = [
        {
            "doc_id": c["doc_id"],
            "section_id": c["section_id"],
            "section_title": c["section_title"],
            "page": "null",  # Chroma requires string/int/float/bool, not None
            "version": c["version"],
            "last_reviewed": c["last_reviewed"],
            "citation": c["citation"],
        }
        for c in chunks
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadatas,
    )
    print(f"Added {collection.count()} chunks to Chroma collection '{COLLECTION_NAME}'.")

    # 5. Build SQLite FTS5 index
    if FTS_PATH.exists():
        FTS_PATH.unlink()

    print(f"Building SQLite FTS5 index at: {FTS_PATH}")
    conn = sqlite3.connect(str(FTS_PATH))
    cur = conn.cursor()
    cur.execute("""
        CREATE VIRTUAL TABLE chunks_fts USING fts5(
            chunk_id UNINDEXED,
            doc_id UNINDEXED,
            section_id UNINDEXED,
            section_title,
            version UNINDEXED,
            last_reviewed UNINDEXED,
            citation UNINDEXED,
            text
        );
    """)

    for c in chunks:
        cur.execute(
            """
            INSERT INTO chunks_fts (
                chunk_id, doc_id, section_id, section_title, version, last_reviewed, citation, text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                c["chunk_id"],
                c["doc_id"],
                c["section_id"],
                c["section_title"],
                c["version"],
                c["last_reviewed"],
                c["citation"],
                c["text"],
            ),
        )
    conn.commit()
    conn.close()
    print(f"Indexed {len(chunks)} chunks into SQLite FTS5 table 'chunks_fts'.")

    total_build_time = time.time() - start_time
    chroma_size = get_dir_size_bytes(CHROMA_DIR)
    fts_size = FTS_PATH.stat().st_size if FTS_PATH.exists() else 0

    print("\n--- Index Build Summary ---")
    print(f"Total build time: {total_build_time:.2f} s")
    print(f"Chroma index directory size: {chroma_size / 1024:.1f} KB ({chroma_size} bytes)")
    print(f"SQLite FTS5 database size: {fts_size / 1024:.1f} KB ({fts_size} bytes)")
    print(f"Total local-index size: {(chroma_size + fts_size) / 1024:.1f} KB")

    return {
        "fts5_supported": fts5_ok,
        "chunk_count": len(chunks),
        "build_time_s": round(total_build_time, 2),
        "chroma_size_bytes": chroma_size,
        "fts_size_bytes": fts_size,
    }


if __name__ == "__main__":
    build_indexes()
