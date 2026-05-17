"""
ranking/scorer.py
-----------------
Scores and ranks nearby emergency facilities fetched from the DB.
Input : list of facility dicts + user lat/lon
Output: same list, sorted by descending composite score

Scoring formula (all components in [0, 1]):
    score = w_dist * distance_score
          + w_rate * rating_score
          + w_resp * response_time_score
          + w_avail * availability_score

Weights are tunable — adjust based on user feedback or judging criteria.

ASSUMPTION: DB fields are named as documented below.
Update _FIELD_MAP if Member 4's schema differs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import math

# ---------------------------------------------------------------------------
# DB field name mapping — change here if schema differs, nowhere else
# ---------------------------------------------------------------------------
_FIELD_MAP = {
    "lat":           "latitude",
    "lon":           "longitude",
    "rating":        "rating",           # float, 0–5
    "response_time": "response_time_min", # int/float, minutes; None if unknown
    "available":     "is_available",      # bool or 0/1
    "name":          "name",
    "type":          "facility_type",
    "phone":         "phone",
    "address":       "address",
}

# ---------------------------------------------------------------------------
# Severity-based weight presets
#
# MINOR   : cuts, bruises, broken limbs — get help fast, distance matters most
# SERIOUS : internal bleeding, head injury, unconscious — quality over speed
# DEFAULT : unknown situation — balanced
#
# Logic: in fatal/serious cases, a mediocre hospital 2 km away is worse than
# a trauma centre 8 km away. Weights reflect this.
# ---------------------------------------------------------------------------
SEVERITY_WEIGHTS = {
    "minor": {
        "distance":      0.55,   # get there fast
        "rating":        0.15,
        "response_time": 0.20,
        "availability":  0.10,
    },
    "serious": {
        "distance":      0.25,   # quality over proximity
        "rating":        0.45,   # best medical care
        "response_time": 0.20,
        "availability":  0.10,
    },
    "default": {
        "distance":      0.40,
        "rating":        0.25,
        "response_time": 0.20,
        "availability":  0.15,
    },
}

# Validate all presets sum to 1.0
for _sev, _w in SEVERITY_WEIGHTS.items():
    assert abs(sum(_w.values()) - 1.0) < 1e-6, f"Weights for '{_sev}' must sum to 1.0"

# Default export — used when no severity is passed
WEIGHTS = SEVERITY_WEIGHTS["default"]


def get_weights(severity: str = "default") -> dict:
    """
    Returns weight dict for a given severity level.
    Falls back to 'default' if an unrecognised severity is passed.

    severity options: 'minor', 'serious', 'default'
    """
    return SEVERITY_WEIGHTS.get(severity, SEVERITY_WEIGHTS["default"])

# ---------------------------------------------------------------------------
# Tuning constants
# ---------------------------------------------------------------------------
MAX_USEFUL_DISTANCE_KM  = 30.0   # beyond this, distance_score → 0 smoothly
MAX_USEFUL_RESPONSE_MIN = 60.0   # beyond 60 min response, score → 0
DEFAULT_RATING          = 3.0    # fallback when rating is NULL
UNAVAILABLE_PENALTY     = 0.4    # availability_score when facility is closed/unknown


# ---------------------------------------------------------------------------
# Haversine — kept local so scorer has zero external deps at import time
# ---------------------------------------------------------------------------
def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# Component scorers — each returns a float in [0, 1]
# ---------------------------------------------------------------------------
def _distance_score(distance_km: float) -> float:
    """
    Exponential decay: score = exp(-k * d)
    k is chosen so that score ≈ 0.05 at MAX_USEFUL_DISTANCE_KM.
    Closer is always better.
    """
    k = math.log(20) / MAX_USEFUL_DISTANCE_KM   # ≈ 0.0998 for 30 km
    return math.exp(-k * distance_km)


def _rating_score(rating: Optional[float]) -> float:
    """Linear 0–5 → 0–1. Null rating gets a neutral DEFAULT_RATING."""
    r = rating if rating is not None else DEFAULT_RATING
    r = max(0.0, min(5.0, r))   # clamp
    return r / 5.0


def _response_time_score(response_time_min: Optional[float]) -> float:
    """
    Inverse linear: faster = higher score.
    None → neutral mid-score (0.5) — unknown is not the same as slow.
    """
    if response_time_min is None:
        return 0.5
    t = max(0.0, response_time_min)
    if t >= MAX_USEFUL_RESPONSE_MIN:
        return 0.0
    return 1.0 - (t / MAX_USEFUL_RESPONSE_MIN)


def _availability_score(available) -> float:
    """
    True/1  → 1.0  (confirmed open)
    False/0 → 0.0  (confirmed closed — still shown but ranked low)
    None    → UNAVAILABLE_PENALTY (unknown — partial credit)
    """
    if available is None:
        return UNAVAILABLE_PENALTY
    return 1.0 if bool(available) else 0.0


# ---------------------------------------------------------------------------
# Main public API
# ---------------------------------------------------------------------------
@dataclass
class ScoredFacility:
    raw: dict                           # original DB row, unchanged
    distance_km: float
    score: float
    breakdown: dict = field(default_factory=dict)   # per-component scores


def score_facilities(
    facilities: list[dict],
    user_lat: float,
    user_lon: float,
    weights: dict[str, float] = WEIGHTS,
) -> list[ScoredFacility]:
    """
    Score and rank a list of facility dicts from the DB.

    Parameters
    ----------
    facilities : raw rows from Supabase / Room DB query
    user_lat, user_lon : caller's GPS coordinates
    weights : override default weights for A/B testing

    Returns
    -------
    List of ScoredFacility, sorted best → worst.
    Empty list if facilities is empty.
    """
    if not facilities:
        return []

    scored: list[ScoredFacility] = []

    for fac in facilities:
        # --- resolve field names via map ---
        fac_lat  = fac.get(_FIELD_MAP["lat"])
        fac_lon  = fac.get(_FIELD_MAP["lon"])

        if fac_lat is None or fac_lon is None:
            # Can't score without coordinates — skip silently
            continue

        dist_km  = _haversine_km(user_lat, user_lon, fac_lat, fac_lon)
        rating   = fac.get(_FIELD_MAP["rating"])
        resp_t   = fac.get(_FIELD_MAP["response_time"])
        avail    = fac.get(_FIELD_MAP["available"])

        d_score  = _distance_score(dist_km)
        r_score  = _rating_score(rating)
        rt_score = _response_time_score(resp_t)
        av_score = _availability_score(avail)

        composite = (
            weights["distance"]      * d_score
            + weights["rating"]      * r_score
            + weights["response_time"] * rt_score
            + weights["availability"]  * av_score
        )

        scored.append(ScoredFacility(
            raw=fac,
            distance_km=round(dist_km, 2),
            score=round(composite, 4),
            breakdown={
                "distance":      round(d_score, 4),
                "rating":        round(r_score, 4),
                "response_time": round(rt_score, 4),
                "availability":  round(av_score, 4),
            }
        ))

    scored.sort(key=lambda x: x.score, reverse=True)
    return scored


def to_api_response(scored: list[ScoredFacility]) -> list[dict]:
    """
    Flatten ScoredFacility list into JSON-serialisable dicts for FastAPI.
    Alokesh plugs this into the /nearby endpoint response.
    """
    result = []
    for sf in scored:
        row = dict(sf.raw)          # copy original fields
        row["distance_km"] = sf.distance_km
        row["score"]       = sf.score
        row["score_breakdown"] = sf.breakdown
        result.append(row)
    return result


# ---------------------------------------------------------------------------
# Smoke test — remove before committing (or keep behind __name__ guard)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    MOCK_FACILITIES = [
        {
            "name": "GMCH Guwahati",
            "facility_type": "hospital",
            "latitude": 26.1445,
            "longitude": 91.7362,
            "rating": 4.2,
            "response_time_min": 8,
            "is_available": True,
            "phone": "0361-2529457",
            "address": "Bhangagarh, Guwahati"
        },
        {
            "name": "Downtown Hospital",
            "facility_type": "hospital",
            "latitude": 26.1358,
            "longitude": 91.7985,
            "rating": 4.5,
            "response_time_min": None,   # unknown
            "is_available": True,
            "phone": "0361-2331003",
            "address": "Dispur, Guwahati"
        },
        {
            "name": "City Nursing Home",
            "facility_type": "clinic",
            "latitude": 26.1510,
            "longitude": 91.7200,
            "rating": None,              # no rating in DB
            "response_time_min": 22,
            "is_available": False,       # closed
            "phone": "9876543210",
            "address": "Fancy Bazar"
        },
    ]

    USER_LAT, USER_LON = 26.1480, 91.7500   # somewhere in Guwahati

    for severity in ["minor", "serious", "default"]:
        weights = get_weights(severity)
        results = score_facilities(MOCK_FACILITIES, USER_LAT, USER_LON, weights=weights)

        print(f"\n--- Severity: {severity.upper()} ---")
        print(f"{'Rank':<5} {'Name':<25} {'Dist(km)':<10} {'Score':<8}")
        print("-" * 55)
        for i, sf in enumerate(results, 1):
            name = sf.raw[_FIELD_MAP["name"]]
            print(f"{i:<5} {name:<25} {sf.distance_km:<10} {sf.score:<8}")