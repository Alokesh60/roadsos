import sys
import os
import math
import sqlite3

REPO_ROOT = r"D:\Roadsafety\roadsos"
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ai.utils.classifier import classify_emergency, detect_severity, get_canned_test_response, get_suspicious_warning
from ai.embeddings.chroma_setup import semantic_search
from ai.ranking.scorer import score_facilities, to_api_response, get_weights
from ai.chatbot.chain import get_chat_response

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DB_PATH        = r"D:\Roadsafety\roadsos\ai\roadsos.db"
MAX_RADIUS_KM  = 100
WIDE_RADIUS_KM = 500
MAX_CANDIDATES = 50

MEDICAL_KEYWORDS = {
    "accident", "crash", "injured", "injury", "bleeding", "hurt", "pain",
    "unconscious", "ambulance", "hospital", "medical", "emergency", "fire",
    "broke", "broken", "fracture", "wound", "burn", "stroke", "heart",
    "seizure", "faint", "fainted", "trapped", "stuck",
}

MEDICAL_FACILITY_TYPES = {"ambulance", "hospital", "police"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


def _get_local_facilities(lat: float, lon: float, radius_km: float = MAX_RADIUS_KM) -> list:
    """
    Bounding-box pre-filter from SQLite, then exact haversine trim.
    Returns rows sorted nearest-first.
    """
    deg = radius_km / 111.0  # 1 degree latitude ≈ 111 km
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT * FROM facilities
        WHERE latitude  BETWEEN ? AND ?
          AND longitude BETWEEN ? AND ?
        """,
        (lat - deg, lat + deg, lon - deg, lon + deg),
    ).fetchall()
    conn.close()

    facilities = [dict(r) for r in rows]
    facilities = [
        f for f in facilities
        if _haversine_km(lat, lon, f["latitude"], f["longitude"]) <= radius_km
    ]
    facilities.sort(key=lambda f: _haversine_km(lat, lon, f["latitude"], f["longitude"]))
    return facilities


def _enrich_with_semantic_scores(facilities: list, message: str) -> list:
    """
    Fetch semantic scores from ChromaDB and attach them to each facility.
    Facilities not returned by semantic search get score 0.0.
    """
    semantic = semantic_search(message, top_k=30)
    score_map = {f["id"]: f.get("semantic_score", 0.0) for f in semantic}
    for f in facilities:
        f["semantic_score"] = score_map.get(f["id"], 0.0)
    return facilities


def _is_medical_emergency(message: str) -> bool:
    """Returns True if the message contains medical/injury keywords."""
    words = set(message.lower().split())
    return bool(words & MEDICAL_KEYWORDS)


def _filter_by_type(facilities: list, message: str) -> list:
    """
    For medical emergencies, push non-medical facility types to the rear.
    Never drops facilities — just reorders so scoring still has all options.
    """
    if not _is_medical_emergency(message):
        return facilities

    primary, secondary = [], []
    for f in facilities:
        ftype = (f.get("facility_type") or "").lower()
        if any(med in ftype for med in MEDICAL_FACILITY_TYPES):
            primary.append(f)
        else:
            secondary.append(f)

    return primary + secondary


# ---------------------------------------------------------------------------
# Main public API
# ---------------------------------------------------------------------------
def process_emergency(message: str, lat: float, lon: float) -> dict:
    try:
        classification = classify_emergency(message)

        if classification.get("status") == "TEST" or not classification.get("proceed", True):
            return {
                "success": False,
                "status": classification.get("status", "TEST"),
                "guidance": get_canned_test_response(),
                "facilities": [],
            }

        severity = detect_severity(message)

        # Stage 1: geo-first retrieval from SQLite
        candidates = _get_local_facilities(lat, lon, MAX_RADIUS_KM)
        if not candidates:
            # Nothing within 100 km — widen search before giving up
            candidates = _get_local_facilities(lat, lon, WIDE_RADIUS_KM)

        # Stage 2: attach semantic scores for scorer tie-breaking
        if candidates:
            candidates = _enrich_with_semantic_scores(candidates, message)

        # Stage 3: deprioritise irrelevant facility types for medical emergencies
        candidates = _filter_by_type(candidates, message)

        if not candidates:
            guidance = get_chat_response(
                message=message,
                lat=lat,
                lon=lon,
                nearby_facilities=[],
                severity=severity,
            )
            return {
                "success": True,
                "status": classification.get("status", "REAL"),
                "severity": severity,
                "guidance": guidance,
                "facilities": [],
            }

        scored = score_facilities(candidates[:MAX_CANDIDATES], lat, lon, get_weights(severity))
        api_facilities = to_api_response(scored)

        guidance = get_chat_response(
            message=message,
            lat=lat,
            lon=lon,
            nearby_facilities=api_facilities[:5],
            severity=severity,
        )

        if classification.get("status") == "SUSPICIOUS":
            guidance += "\n\n" + get_suspicious_warning()

        return {
            "success": True,
            "status": classification.get("status", "REAL"),
            "severity": severity,
            "guidance": guidance,
            "facilities": api_facilities,
        }

    except Exception as e:
        return {
            "success": False,
            "status": "ERROR",
            "guidance": f"Emergency pipeline failed: {str(e)}",
            "facilities": [],
        }