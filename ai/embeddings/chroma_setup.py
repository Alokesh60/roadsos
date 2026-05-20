"""
embeddings/chroma_setup.py
--------------------------
Semantic search over emergency facilities using ChromaDB +
sentence-transformers (all-MiniLM-L6-v2, English only).

What gets embedded per facility:
    "{name} {facility_type} located at {address}. Services: {services}"

The 'services' field name is mapped via _FIELD_MAP — update the right-side
value when Member 4 confirms the exact column name. Everything else stays.

Public API (what chain.py and Alokesh's backend call):
    build_index(facilities)          → builds/rebuilds ChromaDB collection
    semantic_search(query, top_k)    → returns top_k facility dicts by meaning
    add_facilities(facilities)       → incremental add without full rebuild
"""

from __future__ import annotations

import os
import json
import hashlib
from typing import Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# DB field name mapping — right-side values only, change to match schema
# ---------------------------------------------------------------------------
_FIELD_MAP = {
    "id":       "id",               # unique row identifier
    "name":     "name",
    "type":     "facility_type",
    "address":  "address",
    "services": "services_offered", # ← confirm exact column name with Member 4
}

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MODEL_NAME       = "all-MiniLM-L6-v2"
COLLECTION_NAME  = "roadsos_facilities"
CHROMA_PATH      = os.path.join(os.path.dirname(__file__), "../../chroma_db")
SERVICES_UNKNOWN = "general emergency services"   # fallback if services is NULL


# ---------------------------------------------------------------------------
# Singletons — loaded once, reused across calls
# ---------------------------------------------------------------------------
_model: Optional[SentenceTransformer] = None
_client: Optional[chromadb.PersistentClient] = None
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"[chroma] Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path=CHROMA_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}   # cosine similarity for sentence embeddings
        )
    return _collection


# ---------------------------------------------------------------------------
# Text builder — what gets embedded
# ---------------------------------------------------------------------------
def _build_embed_text(facility: dict) -> str:
    """
    Constructs the string that gets embedded for each facility.
    More descriptive = better semantic search results.
    """
    name     = facility.get(_FIELD_MAP["name"], "Unknown facility")
    ftype    = facility.get(_FIELD_MAP["type"], "facility")
    address  = facility.get(_FIELD_MAP["address"], "")
    services = facility.get(_FIELD_MAP["services"]) or SERVICES_UNKNOWN

    return f"{name} {ftype} located at {address}. Services: {services}"


def _make_doc_id(facility: dict) -> str:
    """
    Stable unique ID for each facility.
    Uses DB id if present; falls back to hash of name+address.
    """
    db_id = facility.get(_FIELD_MAP["id"])
    if db_id is not None:
        return str(db_id)

    raw = f"{facility.get(_FIELD_MAP['name'], '')}{facility.get(_FIELD_MAP['address'], '')}"
    return hashlib.md5(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------
def build_index(facilities: list[dict]) -> int:
    """
    Build (or fully rebuild) the ChromaDB collection from a facility list.
    Call this once when the app starts or when the DB is refreshed.

    Returns number of documents indexed.
    """
    if not facilities:
        print("[chroma] No facilities provided — index not built.")
        return 0

    collection = _get_collection()
    model = _get_model()

    # Clear existing data for a clean rebuild
    if collection.count() > 0:
        collection.delete(where={"_dummy": {"$ne": "x"}})

    texts = [_build_embed_text(f) for f in facilities]
    ids = [_make_doc_id(f) for f in facilities]
    metadatas = [{"raw": json.dumps(f)} for f in facilities]

    embeddings = model.encode(texts, show_progress_bar=False).tolist()

    # ---------------- BATCH INSERT FIX ----------------
    BATCH_SIZE = 5000
    total = 0

    for i in range(0, len(facilities), BATCH_SIZE):
        batch_ids = ids[i:i+BATCH_SIZE]
        batch_embeddings = embeddings[i:i+BATCH_SIZE]
        batch_texts = texts[i:i+BATCH_SIZE]
        batch_metadatas = metadatas[i:i+BATCH_SIZE]

        collection.add(
            ids=batch_ids,
            embeddings=batch_embeddings,
            documents=batch_texts,
            metadatas=batch_metadatas
        )

        total += len(batch_ids)
        print(f"[chroma] Indexed batch {i} to {i + len(batch_ids)}")

    print(f"[chroma] Indexed {total} facilities.")
    return total


def semantic_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Find the top_k most semantically relevant facilities for a query.

    Example queries:
        "trauma centre for head injury"
        "24 hour pharmacy near me"
        "hospital with ICU"
        "towing service"

    Returns list of raw facility dicts (same shape as DB rows),
    ordered by semantic similarity. Empty list if index not built.
    """
    collection = _get_collection()

    if collection.count() == 0:
        print("[chroma] WARNING: Collection is empty. Call build_index() first.")
        return []

    model       = _get_model()
    query_embed = model.encode([query], show_progress_bar=False).tolist()

    results = collection.query(
        query_embeddings=query_embed,
        n_results=min(top_k, collection.count()),
        include=["metadatas", "distances", "documents"]
    )

    facilities = []
    for meta, dist in zip(results["metadatas"][0], results["distances"][0]):
        fac = json.loads(meta["raw"])
        fac["semantic_score"] = round(1 - dist, 4)   # cosine distance → similarity
        facilities.append(fac)

    return facilities


def get_index_size() -> int:
    """Returns number of facilities currently in the index."""
    return _get_collection().count()


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    MOCK_FACILITIES = [
        {
            "id": 1,
            "name": "GMCH Guwahati",
            "facility_type": "hospital",
            "address": "Bhangagarh, Guwahati",
            "services_offered": "trauma care, ICU, neurosurgery, emergency surgery, blood bank",
            "rating": 4.2,
            "phone": "0361-2529457",
        },
        {
            "id": 2,
            "name": "Downtown Hospital",
            "facility_type": "hospital",
            "address": "Dispur, Guwahati",
            "services_offered": "cardiac care, orthopaedics, emergency ward, ambulance",
            "rating": 4.5,
            "phone": "0361-2331003",
        },
        {
            "id": 3,
            "name": "Pratiksha Hospital",
            "facility_type": "hospital",
            "address": "Six Mile, Guwahati",
            "services_offered": "general emergency, X-ray, fracture treatment, ICU",
            "rating": 3.9,
            "phone": "0361-2340003",
        },
        {
            "id": 4,
            "name": "City Towing Service",
            "facility_type": "towing",
            "address": "Paltan Bazar, Guwahati",
            "services_offered": "vehicle towing, roadside assistance, puncture repair",
            "rating": 3.5,
            "phone": "9876012345",
        },
        {
            "id": 5,
            "name": "Guwahati Police Control",
            "facility_type": "police",
            "address": "Panbazar, Guwahati",
            "services_offered": "accident response, traffic control, emergency police assistance",
            "rating": None,
            "phone": "100",
        },
    ]

    print("Building index...")
    count = build_index(MOCK_FACILITIES)
    print(f"Index size: {get_index_size()}\n")

    test_queries = [
        "I have a severe head injury, need neurosurgery",
        "my car broke down, need towing",
        "cardiac arrest, need heart specialist",
        "accident on highway, need police",
        "need ICU immediately",
    ]

    for q in test_queries:
        print(f"\nQuery: '{q}'")
        results = semantic_search(q, top_k=2)
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r['name']} ({r['facility_type']}) — semantic_score: {r['semantic_score']}")