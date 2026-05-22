"""
backend/app/services/chatbot_service.py  —  Windows-compatible, Pathway-architecture

Imports — real AI modules are the source of truth:
    - ai.utils.classifier        → classify_emergency
    - ai.embeddings.chroma_setup → semantic_search
    - ai.ranking.scorer          → score_facilities, get_weights, to_api_response
    - app.services.sqlite_service   → get_all_services (geo filtering done here)
    - app.services.distance_service → calculate_distance (haversine)

Pathway RAGOrchestrator structure preserved exactly.
Argument order fixed: process_emergency_chatbot(message, lat, lon)
"""

import os
import sys
import logging
from typing import Optional

# ---------------------------------------------------------------------------
# Repo-root path injection — allows importing ai.* from anywhere the server
# is launched, as long as cwd is backend/ (uvicorn app.main:app --reload).
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Real AI modules (source of truth)
from ai.utils.classifier import classify_emergency, detect_severity
from ai.embeddings.chroma_setup import semantic_search
from ai.ranking.scorer import score_facilities, get_weights, to_api_response

# Backend helpers — geo only, no AI logic here
from app.services.sqlite_service import get_all_services
from app.services.distance_service import calculate_distance

logger = logging.getLogger(__name__)

MAX_RADIUS_KM  = 100
WIDE_RADIUS_KM = 500

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL   = "llama-3.1-8b-instant"


# -- Geo helpers (replaces app.utils.geo) -------------------------------------

def _bounding_box_query(lat: float, lon: float, radius_km: float) -> list:
    """Filter all services by a lat/lon bounding box approximation."""
    deg = radius_km / 111.0          # 1 degree ˜ 111 km
    all_services = get_all_services()
    return [
        s for s in all_services
        if abs(s.get("latitude", 0) - lat) <= deg
        and abs(s.get("longitude", 0) - lon) <= deg
    ]


def _haversine_filter(facilities: list, lat: float, lon: float, radius_km: float) -> list:
    """Attach distance_km and drop facilities beyond radius."""
    result = []
    for f in facilities:
        dist = calculate_distance(lat, lon, f.get("latitude", 0), f.get("longitude", 0))
        if dist <= radius_km:
            f["distance_km"] = round(dist, 2)
            result.append(f)
    return result


# -- Scoring helper — delegates to ai/ranking/scorer.py ----------------------

def _score_facilities(facilities: list, severity: str, user_lat: float, user_lon: float) -> list:
    """
    Delegate scoring to the real scorer in ai/ranking/scorer.py.

    score_facilities(facilities, user_lat, user_lon, weights) returns a list
    of ScoredFacility dataclasses (raw, distance_km, score, breakdown).
    We flatten them back to dicts via to_api_response() so the rest of the
    pipeline (top5 selection, LLM prompt) continues to work with plain dicts.
    """
    weights = get_weights(severity)                              # severity: 'minor' | 'serious' | 'default'
    scored  = score_facilities(facilities, user_lat, user_lon, weights=weights)  # list[ScoredFacility]
    return to_api_response(scored)                               # list[dict], sorted best → worst


# -- Severity helper — delegates to ai/utils/classifier.detect_severity() ------

def _derive_severity(message: str) -> str:
    """
    Derive severity from the raw message text using keyword detection.
    Uses ai.utils.classifier.detect_severity() — no extra API call.
    Returns: 'serious' | 'minor' | 'default'
    """
    return detect_severity(message)


# -- LLM guidance (replaces app.chatbot.chain) ------------------------------- 

def _generate_guidance(message: str, top5: list, severity: str) -> str:
    """
    Call Groq LLM to generate emergency guidance.
    Only uses phone numbers from the facility data — never invented.
    Falls back to a static string if Groq is unavailable.
    """
    if not GROQ_API_KEY:
        return _static_guidance(top5, severity)

    try:
        import httpx

        facility_lines = "\n".join(
            f"- {f.get('name','?')} ({f.get('type','?')}) | "
            f"{f.get('distance_km','?')} km | "
            f"Phone: {f.get('phone', 'unavailable')}"
            for f in top5
        )

        system_prompt = (
            "You are RoadSoS, an emergency assistant for road accidents in India. "
            "Give concise, calm, actionable guidance. "
            "NEVER invent phone numbers — only use numbers from the facility list provided. "
            "If no phone is listed, say 'call 108'."
        )

        user_prompt = (
            f"Emergency message: {message}\n"
            f"Severity: {severity}\n\n"
            f"Nearby facilities:\n{facility_lines}\n\n"
            "Provide step-by-step guidance."
        )

        response = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
                "max_tokens": 400,
            },
            timeout=15,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    except Exception as e:
        logger.warning(f"[Groq] LLM call failed: {e} — using static fallback")
        return _static_guidance(top5, severity)


def _static_guidance(top5: list, severity: str) -> str:
    """Offline fallback guidance when Groq is unreachable."""
    if not top5:
        return "Emergency detected. Please call 108 immediately."
    nearest = top5[0]
    phone   = nearest.get("phone", "108")
    name    = nearest.get("name", "nearest facility")
    return (
        f"{'SEVERE emergency' if severity == 'high' else 'Emergency'} detected. "
        f"Nearest help: {name} — call {phone}. "
        "Stay calm, do not move injured persons unless there is immediate danger."
    )


# -----------------------------------------------------------------------------
# Pathway RAG Orchestrator
# -----------------------------------------------------------------------------

class PathwayRAGOrchestrator:
    """
    Orchestrates the three-stage retrieval pipeline.

    System diagram:
        Android App
            ?  POST /chatbot
        FastAPI  (main.py — unchanged)
            ?
        PathwayRAGOrchestrator   ? this class
            +-- Stage 1: SQLite bounding box + haversine  (geo_retrieval)
            +-- Stage 2: Vector index semantic scores     (semantic_enrichment)
            +-- Stage 3: Type filter ? scorer ? Groq LLM (rank_and_respond)
    """

    def process(self, message: str, lat: float, lon: float) -> dict:
        """Main entry point. Called by process_emergency_chatbot()."""

        # -- Stage 1: Geo Retrieval --------------------------------------------
        candidates = _bounding_box_query(lat, lon, radius_km=MAX_RADIUS_KM)
        if not candidates:
            logger.info("[RAG Stage 1] Empty at 100km — widening to 500km")
            candidates = _bounding_box_query(lat, lon, radius_km=WIDE_RADIUS_KM)

        candidates = _haversine_filter(candidates, lat, lon, radius_km=MAX_RADIUS_KM)
        candidates.sort(key=lambda f: f.get("distance_km", float("inf")))
        logger.info(f"[RAG Stage 1] {len(candidates)} facilities in range")

        # -- Stage 2: Semantic Enrichment --------------------------------------
        semantic_results = semantic_search(message)           # chroma_service signature: (query: str)
        semantic_map     = {r["name"]: r["semantic_score"] for r in semantic_results}

        for fac in candidates:
            fac["semantic_score"] = semantic_map.get(fac.get("name", ""), 0.0)

        non_zero = sum(1 for f in candidates if f["semantic_score"] > 0)
        logger.info(f"[RAG Stage 2] Semantic scores attached ({non_zero} non-zero)")

        # -- Stage 3: Type Filter ? Score ? LLM -------------------------------
        classification = classify_emergency(message)
        severity       = _derive_severity(message)   # keyword-based, no API call

        candidates = self._filter_by_type(candidates, message)
        scored     = _score_facilities(candidates[:50], severity=severity, user_lat=lat, user_lon=lon)
        top5       = scored[:5]
        guidance   = _generate_guidance(message, top5, severity=severity)

        logger.info(f"[RAG Stage 3] Severity={severity}, Top5 selected, guidance generated")

        return {
            "guidance":   guidance,
            "severity":   severity,
            "facilities": scored,
            "top5":       top5,
        }

    @staticmethod
    def _filter_by_type(facilities: list, message: str) -> list:
        """Pushes medical facilities to front when medical keywords detected."""
        medical_kw = {
            "ambulance", "hospital", "injured", "bleeding",
            "unconscious", "cardiac", "chest", "fracture", "accident", "crash"
        }
        if not any(kw in message.lower() for kw in medical_kw):
            return facilities
        priority  = [f for f in facilities if f.get("type") in ("hospital", "ambulance")]
        secondary = [f for f in facilities if f.get("type") not in ("hospital", "ambulance")]
        return priority + secondary


# Singleton
_orchestrator = PathwayRAGOrchestrator()


# -----------------------------------------------------------------------------
# Public entry point — called by FastAPI /chatbot router
# Argument order: message first, then lat, lon  (matches chatbot.py router)
# -----------------------------------------------------------------------------

async def process_emergency_chatbot(
    message: str,
    latitude: float,
    longitude: float,
    user_id: Optional[str] = None,
) -> dict:
    """
    Drop-in replacement called by chatbot.py router:
        process_emergency_chatbot(request.message, request.latitude, request.longitude)
    """
    classification = classify_emergency(message)
    status  = classification.get("status", "REAL")
    proceed = classification.get("proceed", True)

    if not proceed:
        logger.info(f"[Chatbot] Status={status} — skipping pipeline")
        return {
            "status":    status,
            "guidance":  "This appears to be a test message. In a real emergency, call 108.",
            "facilities": [],
            "top5":      [],
            "severity":  "default",
        }

    result = _orchestrator.process(message, latitude, longitude)
    result["status"] = status

    if status == "SUSPICIOUS":
        result["guidance"] += (
            "\n\n⚠️ Note: This message was flagged as potentially ambiguous. "
            "If this is a real emergency, please call 108 immediately."
        )

    return result

