"""
backend/app/services/chroma_service.py  —  thin shim, source of truth is ai/

This file used to own ChromaDB + SentenceTransformer directly.
The real vector index now lives in ai/embeddings/chroma_setup.py (NumPy-based,
Windows-compatible, no Pathway, no torch DLL issues).

We delegate everything here to avoid duplicating any AI logic in the backend.
"""

import os
import sys

# ---------------------------------------------------------------------------
# Repo-root path injection — same approach as chatbot_service.py
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from ai.embeddings.chroma_setup import semantic_search  # noqa: F401 — re-exported


def semantic_emergency_classification(query: str) -> dict:
    """
    Classifies the emergency type from a query using semantic similarity.
    Delegates to the real NumPy vector index in ai/embeddings/chroma_setup.py.
    Returns the top-matched facility type and name.
    """
    results = semantic_search(query, top_k=1)
    if not results:
        return {
            "detected_service_type": "unknown",
            "recommended_service": "Call 112"
        }
    top = results[0]
    return {
        "detected_service_type": top.get("facility_type", "unknown"),
        "recommended_service":   top.get("name", "nearest facility")
    }