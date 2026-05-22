"""
ai/enrich_phones.py  —  FREE phone number enrichment using Overpass API

Run this AFTER build_db.py has created roadsos.db.
It queries OSM Overpass API for phone numbers attached to ambulance
and hospital nodes/ways near each city bounding box, then writes them
into the existing SQLite rows.

No API key required. Overpass API is free and open.

Usage:
    cd D:\\Roadsafety\\roadsos
    python ai/enrich_phones.py

What it does:
    1. For each city, queries Overpass for all OSM nodes tagged as:
       - emergency=ambulance  OR  amenity=hospital
       that also carry a phone/contact:phone/contact:mobile tag
    2. Matches those OSM results to rows already in roadsos.db
       by name similarity + proximity (within 500m)
    3. Writes the phone number into the `phone` column of matched rows
    4. For rows that still have no phone, inserts a city-level
       fallback ambulance number from a hardcoded India state table
       (these are real, publicly listed state ambulance numbers)

After running this, Pathway's vector index will automatically pick up
the phone numbers on next server start (because pw.io.sqlite.read()
re-reads the table).
"""

import sqlite3
import time
import logging
import os
import json
import math
import re
from typing import Optional
import urllib.request
import urllib.parse

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = os.getenv("ROADSOS_DB_PATH", "ai/roadsos.db")
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# ──────────────────────────────────────────────
# Real, publicly listed state ambulance numbers
# Source: NHM India / state health department directories
# These are the numbers that matter most when OSM has nothing.
# ──────────────────────────────────────────────
STATE_AMBULANCE_NUMBERS = {
    # National
    "national":     "108",    # NHM free ambulance — works in most states
    "national_112": "112",    # Unified emergency (police + ambulance)

    # State-specific 108 operators / alternate numbers
    "assam":        "108",
    "delhi":        "102",    # Delhi also has 102 for obstetric emergencies
    "mumbai":       "108",    # Maharashtra
    "bengaluru":    "108",    # Karnataka
    "chennai":      "108",    # Tamil Nadu (GVK EMRI)
    "kolkata":      "108",    # West Bengal
    "hyderabad":    "108",    # Telangana
    "pune":         "108",    # Maharashtra
    "jaipur":       "108",    # Rajasthan
    "ahmedabad":    "108",    # Gujarat

    # City-level known ambulance services with real numbers
    # (cross-referenced from public directories)
    "guwahati":             "108",
    "guwahati_private":     "0361-2529457",   # Gauhati Medical College
    "delhi_aiims":          "011-26588500",
    "delhi_safdarjung":     "011-26707444",
    "mumbai_bmc":           "022-23087000",
    "mumbai_nanavati":      "022-26100000",
    "chennai_govt":         "044-25305000",
    "kolkata_sskm":         "033-22041763",
}

# City → (center_lat, center_lon, search_radius_km)
CITY_BOXES = {
    "guwahati":  (26.1445, 91.7362, 15),
    "delhi":     (28.6139, 77.2090, 25),
    "mumbai":    (19.0760, 72.8777, 20),
    "bengaluru": (12.9716, 77.5946, 20),
    "chennai":   (13.0827, 80.2707, 20),
    "kolkata":   (22.5726, 88.3639, 20),
    "hyderabad": (17.3850, 78.4867, 20),
    "pune":      (18.5204, 73.8567, 15),
    "jaipur":    (26.9124, 75.7873, 15),
    "ahmedabad": (23.0225, 72.5714, 15),
}


# ──────────────────────────────────────────────
# Overpass query helpers
# ──────────────────────────────────────────────

def _build_overpass_query(lat: float, lon: float, radius_m: int) -> str:
    """
    Queries OSM for hospitals and ambulance stations with phone tags
    within radius_m metres of (lat, lon).
    Uses three phone tag variants because OSM contributors are inconsistent.
    """
    return f"""
[out:json][timeout:60];
(
  node["amenity"="hospital"]["phone"](around:{radius_m},{lat},{lon});
  node["amenity"="hospital"]["contact:phone"](around:{radius_m},{lat},{lon});
  node["amenity"="hospital"]["contact:mobile"](around:{radius_m},{lat},{lon});
  way["amenity"="hospital"]["phone"](around:{radius_m},{lat},{lon});
  way["amenity"="hospital"]["contact:phone"](around:{radius_m},{lat},{lon});
  node["emergency"="ambulance_station"]["phone"](around:{radius_m},{lat},{lon});
  node["emergency"="ambulance_station"]["contact:phone"](around:{radius_m},{lat},{lon});
  way["emergency"="ambulance_station"]["phone"](around:{radius_m},{lat},{lon});
);
out center tags;
"""


def _query_overpass(query: str) -> list:
    """Sends query to Overpass API, returns list of OSM elements."""
    encoded = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(
        OVERPASS_URL,
        data=encoded,
        headers={"User-Agent": "RoadSoS-PhoneEnricher/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read())
            return data.get("elements", [])
    except Exception as e:
        logger.warning(f"Overpass query failed: {e}")
        return []


def _extract_phone(tags: dict) -> Optional[str]:
    """Pulls the best phone number from an OSM tags dict."""
    for key in ("phone", "contact:phone", "contact:mobile", "telephone"):
        val = tags.get(key, "").strip()
        if val:
            # Normalise: keep digits, +, spaces, hyphens
            cleaned = re.sub(r"[^\d\+\-\s]", "", val).strip()
            if len(re.sub(r"\D", "", cleaned)) >= 7:   # at least 7 digits
                return cleaned
    return None


def _haversine_m(lat1, lon1, lat2, lon2) -> float:
    """Returns distance in metres between two coordinates."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _name_similarity(a: str, b: str) -> float:
    """
    Rough word-overlap similarity. Good enough for matching
    "Gauhati Medical College Hospital" with "Gauhati Medical College".
    """
    a_words = set(a.lower().split())
    b_words = set(b.lower().split())
    if not a_words or not b_words:
        return 0.0
    overlap = a_words & b_words
    # remove noise words
    noise = {"the", "of", "and", "a", "in", "at", "near", "hospital", "centre", "center"}
    meaningful = overlap - noise
    return len(meaningful) / max(len(a_words - noise), len(b_words - noise), 1)


# ──────────────────────────────────────────────
# DB update helpers
# ──────────────────────────────────────────────

def _get_facilities_needing_phone(conn: sqlite3.Connection, facility_types: tuple) -> list:
    """Returns facilities that have no phone number yet."""
    cur = conn.cursor()
    placeholders = ",".join("?" * len(facility_types))
    cur.execute(f"""
        SELECT id, name, latitude, longitude, facility_type
        FROM facilities
        WHERE (phone IS NULL OR phone = '')
          AND facility_type IN ({placeholders})
    """, facility_types)
    return [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]


def _write_phone(conn: sqlite3.Connection, facility_id: int, phone: str):
    conn.execute(
        "UPDATE facilities SET phone = ? WHERE id = ?",
        (phone, facility_id)
    )


# ──────────────────────────────────────────────
# Main enrichment logic
# ──────────────────────────────────────────────

def enrich_from_overpass(conn: sqlite3.Connection):
    """
    For each city, fetches OSM phone-tagged hospitals/ambulance stations
    and matches them to existing DB rows by proximity + name similarity.
    """
    logger.info("=== Phase 1: Overpass API phone enrichment ===")

    facilities = _get_facilities_needing_phone(conn, ("hospital", "ambulance"))
    logger.info(f"Facilities needing phone: {len(facilities)}")

    for city, (clat, clon, radius_km) in CITY_BOXES.items():
        logger.info(f"Querying Overpass for {city} …")
        query   = _build_overpass_query(clat, clon, radius_km * 1000)
        osm_elements = _query_overpass(query)
        logger.info(f"  → {len(osm_elements)} OSM results with phone tags")

        # Build lookup: list of (osm_lat, osm_lon, phone, name)
        osm_phones = []
        for el in osm_elements:
            tags = el.get("tags", {})
            phone = _extract_phone(tags)
            if not phone:
                continue
            # Ways have a 'center' key; nodes have lat/lon directly
            if "center" in el:
                elat, elon = el["center"]["lat"], el["center"]["lon"]
            else:
                elat, elon = el.get("lat", 0), el.get("lon", 0)
            osm_phones.append({
                "lat":   elat,
                "lon":   elon,
                "phone": phone,
                "name":  tags.get("name", ""),
            })

        if not osm_phones:
            continue

        # Match to DB facilities in this city's radius
        city_facilities = [
            f for f in facilities
            if _haversine_m(f["latitude"], f["longitude"], clat, clon) <= radius_km * 1000
        ]

        matched = 0
        for fac in city_facilities:
            if fac.get("_phone_set"):
                continue
            best_score  = 0
            best_phone  = None
            for osm in osm_phones:
                dist = _haversine_m(fac["latitude"], fac["longitude"], osm["lat"], osm["lon"])
                if dist > 500:      # must be within 500m
                    continue
                name_sim = _name_similarity(fac["name"], osm["name"])
                # Combined score: proximity + name overlap
                prox_score = max(0, 1 - dist / 500)
                combined   = 0.6 * prox_score + 0.4 * name_sim
                if combined > best_score:
                    best_score = combined
                    best_phone = osm["phone"]

            if best_phone and best_score > 0.3:
                _write_phone(conn, fac["id"], best_phone)
                fac["_phone_set"] = True
                matched += 1

        logger.info(f"  → matched phone numbers for {matched} facilities in {city}")
        time.sleep(2)   # be polite to Overpass rate limits

    conn.commit()
    logger.info("Phase 1 complete.")


def enrich_with_state_fallbacks(conn: sqlite3.Connection):
    """
    For ambulance facilities that still have no phone after Overpass,
    assign the city/state 108 number as a fallback.
    This guarantees every ambulance row has at least one callable number.
    """
    logger.info("=== Phase 2: State/city fallback numbers ===")

    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, latitude, longitude, facility_type, address
        FROM facilities
        WHERE (phone IS NULL OR phone = '')
          AND facility_type = 'ambulance'
    """)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    facilities = [dict(zip(cols, r)) for r in rows]
    logger.info(f"Ambulance facilities still without phone: {len(facilities)}")

    # Assign city-specific fallback based on coordinates
    for fac in facilities:
        fac_lat, fac_lon = fac["latitude"], fac["longitude"]
        best_city  = None
        best_dist  = float("inf")
        for city, (clat, clon, _) in CITY_BOXES.items():
            d = _haversine_m(fac_lat, fac_lon, clat, clon)
            if d < best_dist:
                best_dist  = d
                best_city  = city

        phone = STATE_AMBULANCE_NUMBERS.get(best_city, "108")
        _write_phone(conn, fac["id"], phone)

    conn.commit()
    logger.info(f"Phase 2 complete: assigned fallback numbers to {len(facilities)} ambulances")


def enrich_hospitals_fallback(conn: sqlite3.Connection):
    """
    For hospitals still without a phone, assign the city's general
    ambulance/emergency number so there's always something to call.
    """
    logger.info("=== Phase 3: Hospital fallback numbers ===")

    cur = conn.cursor()
    cur.execute("""
        SELECT id, latitude, longitude FROM facilities
        WHERE (phone IS NULL OR phone = '')
          AND facility_type = 'hospital'
    """)
    rows = cur.fetchall()
    logger.info(f"Hospitals still without phone: {len(rows)}")

    for row in rows:
        fid, flat, flon = row
        best_city = min(
            CITY_BOXES.keys(),
            key=lambda c: _haversine_m(flat, flon, CITY_BOXES[c][0], CITY_BOXES[c][1])
        )
        # For hospitals without a direct number, 108 is the correct
        # dispatch fallback — they can route to the right facility
        phone = STATE_AMBULANCE_NUMBERS.get(best_city, "108")
        _write_phone(conn, fid, phone)

    conn.commit()
    logger.info(f"Phase 3 complete: {len(rows)} hospitals assigned fallback")


def print_summary(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("""
        SELECT facility_type,
               COUNT(*) as total,
               SUM(CASE WHEN phone IS NOT NULL AND phone != '' THEN 1 ELSE 0 END) as has_phone
        FROM facilities
        GROUP BY facility_type
    """)
    logger.info("\n── Phone coverage after enrichment ──")
    logger.info(f"{'Type':<15} {'Total':>7} {'Has Phone':>10} {'Coverage':>10}")
    logger.info("─" * 45)
    for row in cur.fetchall():
        ftype, total, has_phone = row
        pct = (has_phone / total * 100) if total else 0
        logger.info(f"{ftype:<15} {total:>7} {has_phone:>10} {pct:>9.1f}%")


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        logger.error(f"Database not found at {DB_PATH}. Run build_db.py first.")
        raise SystemExit(1)

    conn = sqlite3.connect(DB_PATH)

    # Add phone column if it doesn't exist yet
    try:
        conn.execute("ALTER TABLE facilities ADD COLUMN phone TEXT DEFAULT ''")
        conn.commit()
        logger.info("Added 'phone' column to facilities table")
    except sqlite3.OperationalError:
        pass   # column already exists — fine

    enrich_from_overpass(conn)        # Phase 1: real numbers from OSM
    enrich_with_state_fallbacks(conn) # Phase 2: 108 for ambulances with nothing
    enrich_hospitals_fallback(conn)   # Phase 3: 108 for hospitals with nothing
    print_summary(conn)

    conn.close()
    logger.info("\nDone. roadsos.db is now enriched with phone numbers.")
    logger.info("Pathway's vector index will pick up the new data on next server start.")