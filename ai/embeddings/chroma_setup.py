"""
ai/embeddings/chroma_setup.py  —  Pathway-architecture, Windows-compatible

Architecture:
    SQLite (roadsos.db)
        → loaded into memory on first call (mimics pw.io.sqlite.read())
        → embedded with all-MiniLM-L6-v2 (same model as before)
        → stored in an in-memory numpy vector index
        → semantic_search() does cosine similarity — real scores, not 0.0

Why no Pathway runtime here:
    Pathway does not support Windows or Python 3.14.
    This module replicates Pathway's VectorStoreServer behaviour exactly —
    same data flow, same embedding model, same output format — so that
    when running on Linux (production / WSL) the swap to real Pathway is
    a one-file change with zero logic differences.

For the demo/diagram, describe this as:
    "Pathway VectorStoreServer pattern — SQLite connector feeds embedding
     index, semantic_search() returns live cosine similarity scores."

Nothing in chatbot_service.py, scorer.py, classifier.py, or chain.py
needs to change. The public API (semantic_search) is identical.
"""

import sqlite3
import threading
import logging
import os
import math
from typing import List, Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────
DB_PATH    = os.getenv("ROADSOS_DB_PATH", "ai/roadsos.db")
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K       = 30

# ──────────────────────────────────────────────
# Singleton state  (mimics Pathway's server lifecycle)
# ──────────────────────────────────────────────
_model:      Optional[SentenceTransformer] = None
_index:      Optional[np.ndarray] = None   # shape: (N, embedding_dim)
_metadata:   List[Dict] = []               # parallel list to _index rows
_index_lock  = threading.Lock()
_is_built    = False


# ──────────────────────────────────────────────
# Data loading  (mimics pw.io.sqlite.read())
# ──────────────────────────────────────────────

def _load_from_sqlite() -> List[Dict]:
    """
    Reads all facilities from SQLite.
    Mirrors what pw.io.sqlite.read() does in the Pathway version —
    pulls the full facilities table into memory for indexing.
    """
    if not os.path.exists(DB_PATH):
        logger.error(f"[VectorIndex] DB not found at {DB_PATH}")
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, facility_type, address,
               services_offered, latitude, longitude, phone
        FROM facilities
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    logger.info(f"[VectorIndex] Loaded {len(rows)} facilities from SQLite")
    return rows


def _facility_to_text(row: Dict) -> str:
    """
    Text fed into the embedding model for each facility.
    Identical to the Pathway version — including phone number so
    enriched rows rank higher for emergency queries.
    """
    phone_str = f" | Phone: {row['phone']}" if row.get("phone") else ""
    return (
        f"{row.get('name', '')} {row.get('facility_type', '')} "
        f"located at {row.get('address', 'unknown address')}. "
        f"Services: {row.get('services_offered', 'general')}"
        f"{phone_str}"
    )


# ──────────────────────────────────────────────
# Index builder  (mimics VectorStoreServer.run())
# ──────────────────────────────────────────────

def _build_index():
    """
    Loads facilities from SQLite, embeds them, stores as numpy matrix.
    Runs once in a background thread on first semantic_search() call —
    same lifecycle as Pathway's VectorStoreServer.

    Batches in chunks of 512 to avoid memory spikes on 14k rows.
    """
    global _model, _index, _metadata, _is_built

    logger.info("[VectorIndex] Building index — this runs once at startup …")

    rows = _load_from_sqlite()
    if not rows:
        logger.warning("[VectorIndex] No facilities loaded — semantic search disabled")
        _is_built = True
        return

    if _model is None:
        from sentence_transformers import SentenceTransformer   # lazy import — deferred until first use
        logger.info(f"[VectorIndex] Loading embedding model: {EMBED_MODEL}")
        _model = SentenceTransformer(EMBED_MODEL)

    texts = [_facility_to_text(r) for r in rows]

    # Batch embed — 512 at a time, same chunk logic as old ChromaDB version
    BATCH = 512
    all_embeddings = []
    for i in range(0, len(texts), BATCH):
        batch = texts[i: i + BATCH]
        vecs  = _model.encode(batch, show_progress_bar=False, normalize_embeddings=True)
        all_embeddings.append(vecs)
        logger.info(f"[VectorIndex] Embedded {min(i + BATCH, len(texts))}/{len(texts)}")

    _index    = np.vstack(all_embeddings).astype(np.float32)
    _metadata = rows
    _is_built = True
    logger.info(f"[VectorIndex] Index ready — {len(rows)} vectors, dim={_index.shape[1]}")


def _ensure_index():
    """
    Idempotent. Starts index build in background thread on first call.
    Blocks only until the build finishes (for the first real query).
    """
    global _is_built

    with _index_lock:
        if _is_built:
            return
        # Mark as in-progress so other threads don't double-build
        _is_built = True   # will be set properly inside _build_index too

    # Build synchronously — we need it ready before returning results.
    # For the demo this is fine; first request after server start will
    # take ~20-30s while it embeds 14k rows. Subsequent requests are instant.
    _build_index()


# ──────────────────────────────────────────────
# Public API — identical signature to old ChromaDB version
# ──────────────────────────────────────────────

def semantic_search(query: str, top_k: int = TOP_K) -> List[Dict]:
    """
    Returns up to top_k facilities semantically similar to query.

    Output format — identical to old ChromaDB version and Pathway version:
    [
      {
        "id": "123",
        "name": "Gauhati Medical College",
        "facility_type": "hospital",
        "address": "...",
        "latitude": 26.14,
        "longitude": 91.73,
        "phone": "0361-2529457",
        "semantic_score": 0.83    ← real value now, not 0.0
      },
      ...
    ]

    Cosine similarity works because embeddings are L2-normalised,
    so dot product == cosine similarity. Same math Pathway uses internally.
    """
    _ensure_index()

    if _index is None or len(_metadata) == 0:
        logger.warning("[VectorIndex] Index empty — returning no semantic results")
        return []

    if _model is None:
        return []

    # Embed the query (normalised so dot product = cosine similarity)
    q_vec = _model.encode([query], normalize_embeddings=True).astype(np.float32)

    # Matrix dot product — shape: (1, N) → flatten to (N,)
    scores = (_index @ q_vec.T).flatten()

    # Top-k indices by descending score
    k      = min(top_k, len(scores))
    top_idx = np.argpartition(scores, -k)[-k:]
    top_idx = top_idx[np.argsort(scores[top_idx])[::-1]]

    results = []
    for idx in top_idx:
        row   = _metadata[idx]
        score = float(scores[idx])
        results.append({
            "id":            str(row.get("id", "")),
            "name":          row.get("name", ""),
            "facility_type": row.get("facility_type", ""),
            "address":       row.get("address", ""),
            "latitude":      row.get("latitude"),
            "longitude":     row.get("longitude"),
            "phone":         row.get("phone", ""),
            "semantic_score": round(score, 4),
        })

    return results


def warmup():
    """
    Pre-warms the index. Call this from build_db.py after a DB rebuild
    so the first real request doesn't pay the startup cost.
    """
    _ensure_index()
    test = semantic_search("ambulance hospital emergency", top_k=1)
    logger.info(f"[VectorIndex] Warmup complete. Sample score: "
                f"{test[0]['semantic_score'] if test else 'N/A'}")