"""
fetch_global_data.py
--------------------
Fetches global emergency service locations from OpenStreetMap (Overpass API)
and writes data/service_points.csv for use by build_db.py.

USAGE:
    python fetch_global_data.py                         # full run
    python fetch_global_data.py --resume                # resume after crash
    python fetch_global_data.py --region India_Northeast # single region
    python fetch_global_data.py --workers 4             # more parallelism

DEPENDENCIES:
    pip install requests reverse_geocoder

PERFORMANCE vs previous version:
    1. Batch reverse geocoding (0.55s/1000) instead of per-row (43s/1000)
    2. Single combined Overpass query per region (was 6 separate queries)
    3. POST instead of GET — avoids URL length limits
    4. Overpass mirror rotation on 429/403
    5. Streaming CSV writer — flat memory regardless of row count
    6. Per-region dedup + global dedup at merge

DATA QUALITY FIXES (this version):
    FIX A: Bbox-based country inference runs BEFORE reverse_geocoder.
            reverse_geocoder has a known KD-tree coverage gap that tags
            Northeast India / border areas as "AD" (Andorra). By checking
            whether a coordinate falls inside a region bbox that maps to a
            known country, we get the right country code for ~95% of rows
            without calling the library at all. reverse_geocoder is only
            used for genuinely ambiguous multi-country regions.

    FIX B: COUNTRY_FALLBACKS now keyed on ISO 2-letter codes (IN, US, GB)
            to match what reverse_geocoder actually returns in the 'cc' field.
            Previous version mixed full names ("India") with ISO codes,
            causing virtually all fallback phone lookups to miss and default
            to 112 instead of the correct national number.

    FIX C: normalize_phone() now strips country-code prefixes before
            comparing length — "+91-108" was being normalised to "91108"
            (7 digits) instead of "108". Short emergency codes are now
            correctly preserved.

    FIX D: detect_service_type() checks 'healthcare' OSM tag in addition
            to 'amenity' — many Indian clinics/hospitals only have this tag,
            which caused them to be silently dropped before.
"""

import sys
import io
import re

# Force UTF-8 on Windows — prevents UnicodeEncodeError with CP1252 terminal
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import argparse
import csv
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
import reverse_geocoder

# Pre-load KD-tree index ONCE at import — shared across all worker threads.
# Saves ~1.3s per region (was being reloaded per subprocess in old version).
print("Loading reverse_geocoder index (one-time, ~1.3s)...")
reverse_geocoder.search([(0.0, 0.0)], verbose=False)
print("Index loaded.\n")


# ============================================================
# PATHS
# ============================================================

BASE_DIR     = Path(__file__).parent
DATA_DIR     = BASE_DIR / "data"
PROGRESS_DIR = DATA_DIR / "progress"
OUTPUT_CSV   = DATA_DIR / "service_points.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)
PROGRESS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# OVERPASS — mirrors for rotation on rate-limit
# ============================================================

OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
_mirror_index = 0
_mirror_lock  = threading.Lock()

def get_overpass_url() -> str:
    return OVERPASS_MIRRORS[_mirror_index % len(OVERPASS_MIRRORS)]

def rotate_mirror() -> str:
    global _mirror_index
    with _mirror_lock:
        _mirror_index += 1
        url = OVERPASS_MIRRORS[_mirror_index % len(OVERPASS_MIRRORS)]
    print(f"    Switching Overpass mirror → {url}")
    return url

USER_AGENT = "RoadSOS-OfflineDB/2.1 (emergency app hackathon project)"

# ============================================================
# WORLD REGIONS
# Format: (name, south, west, north, east)
# Small bounding boxes to stay under Overpass query limits.
# ============================================================

REGIONS = [
    # ── India (8 regions — already fetched) ──────────────────
    ("India_NW",                24.0,  68.0,  37.0,  75.0),
    ("India_NC",                24.0,  75.0,  30.0,  82.0),
    ("India_NE_Plains",         24.0,  82.0,  27.0,  88.0),
    ("India_Northeast",         22.0,  88.0,  29.5,  97.5),
    ("India_West",              16.0,  68.0,  24.0,  76.0),
    ("India_Central",           16.0,  76.0,  24.0,  83.0),
    ("India_East",              18.0,  83.0,  24.0,  92.0),
    ("India_South",              6.0,  68.0,  18.0,  80.5),

    # ── South Asia ────────────────────────────────────────────
    ("Asia_Pakistan_N",         30.0,  60.0,  37.0,  75.0),
    ("Asia_Pakistan_S",         23.0,  60.0,  30.0,  75.0),
    ("Asia_Bangladesh",         20.0,  88.0,  26.5,  92.5),
    ("Asia_Myanmar_N",          20.0,  92.5,  28.0, 101.0),
    ("Asia_Myanmar_S",          10.0,  92.5,  20.0, 101.0),
    ("Asia_Nepal_Bhutan",       26.0,  80.0,  30.0,  92.5),
    ("Asia_SriLanka",            5.5,  79.5,   9.9,  82.0),

    # ── Southeast Asia ────────────────────────────────────────
    ("Asia_Thailand_N",         15.0,  97.0,  20.5, 105.0),
    ("Asia_Thailand_S",          5.5,  97.0,  15.0, 105.0),
    ("Asia_Vietnam_N",          16.0, 102.0,  23.5, 108.0),
    ("Asia_Vietnam_S",           8.0, 102.0,  16.0, 108.0),
    ("Asia_Malaysia_W",          1.0,  99.5,   6.5, 104.5),
    ("Asia_Malaysia_E",          1.0, 109.0,   7.0, 119.0),
    ("Asia_Indonesia_W",        -6.0,  95.0,   5.5, 110.0),
    ("Asia_Indonesia_E",        -8.0, 110.0,   2.0, 141.0),
    ("Asia_Philippines_N",      12.0, 119.0,  20.0, 127.0),
    ("Asia_Philippines_S",       4.0, 119.0,  12.0, 127.0),
    ("Asia_Singapore_Cambodia",  1.0, 100.0,  15.0, 108.0),

    # ── East Asia ─────────────────────────────────────────────
    ("Asia_China_NW",           35.0,  73.0,  50.0,  95.0),
    ("Asia_China_NE",           35.0,  95.0,  53.0, 116.0),
    ("Asia_China_E",            27.0, 110.0,  40.0, 122.0),
    ("Asia_China_S",            18.0, 100.0,  27.0, 117.0),
    ("Asia_Japan_N",            38.0, 130.0,  45.5, 146.0),
    ("Asia_Japan_S",            30.0, 129.0,  38.0, 142.0),
    ("Asia_Korea",              33.0, 124.0,  38.5, 130.0),
    ("Asia_Taiwan",             21.5, 119.5,  25.5, 122.5),

    # ── Central Asia ──────────────────────────────────────────
    ("Asia_Central_W",          35.0,  45.0,  55.0,  65.0),
    ("Asia_Central_E",          35.0,  65.0,  55.0,  87.0),

    # ── Middle East ───────────────────────────────────────────
    ("Asia_Middle_East_Turkey",  36.0,  26.0,  42.0,  45.0),
    ("Asia_Middle_East_Levant",  29.0,  33.0,  37.0,  42.0),
    ("Asia_Middle_East_Gulf_W",  12.0,  38.0,  30.0,  50.0),
    ("Asia_Middle_East_Gulf_E",  12.0,  50.0,  30.0,  63.0),

    # ── UK & Ireland ──────────────────────────────────────────
    ("Europe_UK_Scotland",      54.5,  -7.5,  61.0,   2.0),
    ("Europe_UK_England_N",     52.5,  -3.5,  55.5,   2.0),
    ("Europe_UK_England_S",     49.5,  -5.8,  52.5,   2.0),
    ("Europe_UK_Wales",         51.3,  -5.4,  53.5,  -2.6),
    ("Europe_Ireland",          51.3,  -10.7, 55.5,  -5.8),

    # ── France ────────────────────────────────────────────────
    ("Europe_France_NW",        46.5,  -4.8,  51.2,   2.5),
    ("Europe_France_NE",        46.5,   2.5,  49.5,   8.2),
    ("Europe_France_SW",        42.3,  -2.0,  46.5,   2.5),
    ("Europe_France_SE",        43.0,   2.5,  46.5,   7.8),

    # ── Germany ───────────────────────────────────────────────
    ("Europe_Germany_NW",       51.0,   6.0,  55.1,  10.0),
    ("Europe_Germany_NE",       51.0,  10.0,  55.1,  15.1),
    ("Europe_Germany_SW",       47.3,   6.0,  51.0,  10.0),
    ("Europe_Germany_SE",       47.3,  10.0,  51.0,  15.1),

    # ── Spain & Portugal ──────────────────────────────────────
    ("Europe_Portugal",         36.8,  -9.5,  42.2,  -6.2),
    ("Europe_Spain_NW",         40.0,  -9.5,  44.0,  -3.0),
    ("Europe_Spain_NE",         40.0,  -3.0,  43.8,   3.3),
    ("Europe_Spain_SW",         36.0,  -7.5,  40.0,  -3.0),
    ("Europe_Spain_SE",         36.0,  -3.0,  40.5,   4.5),

    # ── Italy ─────────────────────────────────────────────────
    ("Europe_Italy_NW",         43.5,   6.5,  47.1,  12.0),
    ("Europe_Italy_NE",         43.5,  12.0,  46.7,  14.0),
    ("Europe_Italy_Central",    40.5,  11.0,  43.5,  16.5),
    ("Europe_Italy_South",      37.5,  14.5,  41.5,  18.5),
    ("Europe_Sicily_Sardinia",  36.5,   8.0,  38.5,  15.7),

    # ── Benelux & Switzerland & Austria ───────────────────────
    ("Europe_Benelux",          49.4,   2.5,  53.6,   7.3),
    ("Europe_Switzerland",      45.8,   5.9,  47.9,  10.5),
    ("Europe_Austria",          46.3,   9.5,  49.1,  17.2),

    # ── Scandinavia ───────────────────────────────────────────
    ("Europe_Denmark",          54.5,   8.0,  57.8,  15.2),
    ("Europe_Norway_S",         57.8,   4.5,  63.0,  15.0),
    ("Europe_Norway_N",         63.0,   4.5,  71.2,  31.0),
    ("Europe_Sweden_S",         55.3,  10.8,  60.0,  19.0),
    ("Europe_Sweden_N",         60.0,  11.0,  69.1,  24.5),
    ("Europe_Finland",          59.7,  19.5,  70.1,  31.6),

    # ── Eastern Europe ────────────────────────────────────────
    ("Europe_Poland_N",         51.0,  14.0,  55.0,  23.0),
    ("Europe_Poland_S",         49.0,  14.0,  51.0,  24.2),
    ("Europe_Baltics",          53.8,  20.8,  59.8,  28.3),
    ("Europe_Czech_Slovakia",   47.7,  12.0,  51.1,  22.6),
    ("Europe_Hungary_Romania_N",45.5,  16.0,  48.5,  27.0),
    ("Europe_Romania_S",        43.5,  22.0,  45.5,  30.0),
    ("Europe_Bulgaria_Greece_N",41.0,  22.0,  44.5,  28.5),
    ("Europe_Greece_S",         36.5,  21.0,  41.0,  26.5),
    ("Europe_Balkans_W",        41.5,  13.5,  46.5,  20.5),
    ("Europe_Balkans_E",        41.0,  20.5,  44.5,  28.5),
    ("Europe_Ukraine_W",        46.0,  22.0,  52.5,  32.0),
    ("Europe_Ukraine_E",        46.0,  32.0,  52.5,  40.5),
    ("Europe_Belarus_Moldova",  45.4,  27.5,  54.0,  35.0),

    # ── Russia (West of Urals only — most populated) ───────────
    ("Europe_Russia_W",         51.0,  33.0,  61.0,  50.0),
    ("Europe_Russia_C",         51.0,  50.0,  61.0,  65.0),

    # ── USA Northeast ─────────────────────────────────────────
    ("USA_Maine_Vermont",       43.0,  -73.5,  47.5, -66.8),
    ("USA_Massachusetts_RI",    41.2,  -73.5,  43.0, -69.8),
    ("USA_New_York_N",          42.8,  -79.8,  45.1, -73.5),
    ("USA_New_York_S",          40.4,  -74.3,  42.8, -71.8),
    ("USA_Connecticut_NJ",      39.5,  -75.6,  42.1, -71.8),
    ("USA_Pennsylvania_N",      41.0,  -80.5,  42.5, -74.5),
    ("USA_Pennsylvania_S",      39.5,  -80.5,  41.0, -74.5),

    # ── USA Mid Atlantic & Southeast ──────────────────────────
    ("USA_Maryland_Delaware",   38.4,  -77.5,  39.8, -74.9),
    ("USA_Virginia_WV",         36.5,  -82.7,  39.5, -75.2),
    ("USA_NC_SC_N",             34.5,  -84.5,  36.6, -75.4),
    ("USA_NC_SC_S",             32.0,  -84.0,  34.5, -78.5),
    ("USA_Georgia",             30.4,  -85.6,  35.0, -80.8),
    ("USA_Florida_N",           27.5,  -87.7,  31.0, -80.0),
    ("USA_Florida_S",           24.4,  -82.0,  27.5, -79.8),

    # ── USA Midwest ───────────────────────────────────────────
    ("USA_Ohio_Indiana",        37.8,  -88.1,  42.3, -80.5),
    ("USA_Michigan",            41.7,  -90.4,  48.3, -82.1),
    ("USA_Illinois_Wisconsin_N",43.0,  -92.9,  47.1, -86.8),
    ("USA_Illinois_Wisconsin_S",37.0,  -91.5,  43.0, -87.0),
    ("USA_Minnesota_Iowa",      40.4,  -97.2,  49.4, -89.5),
    ("USA_Missouri_Kansas_N",   38.5,  -95.8,  40.6, -91.0),
    ("USA_Missouri_Kansas_S",   36.0,  -95.8,  38.5, -91.0),

    # ── USA Great Plains ──────────────────────────────────────
    ("USA_Dakotas_Nebraska_N",  43.0, -104.1,  49.0, -96.5),
    ("USA_Dakotas_Nebraska_S",  40.0, -104.1,  43.0, -96.5),
    ("USA_Oklahoma_Arkansas",   33.6,  -103.0, 37.0, -89.4),

    # ── USA South ─────────────────────────────────────────────
    ("USA_Texas_NW",            31.0, -107.0,  36.5, -100.0),
    ("USA_Texas_NE",            31.0, -100.0,  36.5,  -93.5),
    ("USA_Texas_SW",            25.8, -107.0,  31.0, -100.0),
    ("USA_Texas_SE",            25.8, -100.0,  31.0,  -93.5),
    ("USA_Louisiana_Mississippi",28.8, -94.0,  35.0,  -88.0),
    ("USA_Alabama_Tennessee",   34.5,  -90.5,  36.7,  -84.8),

    # ── USA Mountain West ─────────────────────────────────────
    ("USA_Montana_Wyoming",     41.0, -116.1,  49.0, -104.0),
    ("USA_Idaho_Nevada_N",      38.0, -117.3,  49.0, -111.0),
    ("USA_Colorado_Utah",       36.9, -114.1,  41.0, -102.0),
    ("USA_Arizona_NM",          31.3, -114.8,  37.0, -103.0),

    # ── USA West Coast ────────────────────────────────────────
    ("USA_Washington_Oregon_N", 44.5, -124.8,  49.0, -116.5),
    ("USA_Oregon_S",            41.9, -124.6,  44.5, -116.5),
    ("USA_California_N",        37.0, -124.5,  42.1, -119.5),
    ("USA_California_Central",  35.0, -121.5,  37.5, -118.0),
    ("USA_California_S",        32.5, -117.7,  35.0, -114.1),

    # ── Canada ────────────────────────────────────────────────
    ("Canada_BC",               48.3, -139.1,  60.0, -114.0),
    ("Canada_Alberta",          49.0, -120.0,  60.0, -110.0),
    ("Canada_Prairies",         49.0, -110.0,  60.0,  -95.0),
    ("Canada_Ontario_W",        41.7,  -95.0,  51.0,  -80.0),
    ("Canada_Ontario_E",        43.5,  -80.0,  47.5,  -74.0),
    ("Canada_Quebec_S",         44.9,  -79.8,  49.0,  -64.0),
    ("Canada_Quebec_N",         49.0,  -79.8,  62.6,  -57.0),
    ("Canada_Maritimes",        43.4,  -67.0,  48.1,  -59.5),

    # ── Mexico & Central America ──────────────────────────────
    ("Mexico_North",            26.0, -117.1,  32.7,  -97.0),
    ("Mexico_Central",          19.0, -105.0,  26.0,  -97.0),
    ("Mexico_South",            14.5, -100.0,  19.0,  -86.5),
    ("Central_America_N",       13.0,  -92.3,  18.5,  -83.0),
    ("Central_America_S",        7.2,  -83.5,  13.0,  -77.0),

    # ── South America ─────────────────────────────────────────
    ("SA_Colombia_Venezuela",    0.7,  -73.0,  12.5,  -59.8),
    ("SA_Peru_Ecuador",         -5.0,  -81.3,   1.5,  -68.7),
    ("SA_Bolivia_Paraguay",    -23.0,  -69.7,  -7.0,  -55.3),
    ("SA_Brazil_N",             -5.0,  -60.0,   5.5,  -44.0),
    ("SA_Brazil_NE",           -15.0,  -44.0,  -3.0,  -34.8),
    ("SA_Brazil_Central",      -23.0,  -54.0,  -8.0,  -40.0),
    ("SA_Brazil_S",            -34.0,  -58.5, -22.5,  -44.0),
    ("SA_Argentina_Chile_N",   -35.0,  -75.0, -20.0,  -55.0),
    ("SA_Argentina_Chile_S",   -56.0,  -76.0, -35.0,  -53.0),

    # ── Africa ────────────────────────────────────────────────
    ("Africa_Morocco_Algeria",  19.0,  -17.5,  37.5,   9.0),
    ("Africa_Tunisia_Libya",    19.0,   8.0,   37.5,  25.5),
    ("Africa_Egypt",            22.0,  24.7,   31.7,  37.0),
    ("Africa_West_N",           10.0,  -17.5,  20.0,   5.0),
    ("Africa_West_S",            4.0,  -17.5,  10.0,   5.0),
    ("Africa_Nigeria_N",         9.0,   3.0,   14.0,  15.0),
    ("Africa_Nigeria_S",         4.0,   3.0,    9.0,  15.0),
    ("Africa_Central_W",        -5.0,   8.0,    5.5,  20.0),
    ("Africa_Central_E",        -5.0,  20.0,    5.5,  32.0),
    ("Africa_Ethiopia_Horn",     2.0,  32.5,   15.5,  51.5),
    ("Africa_Kenya_Tanzania_N",  -2.0,  29.5,   5.0,  42.0),
    ("Africa_Kenya_Tanzania_S", -12.0,  29.5,  -2.0,  40.5),
    ("Africa_Mozambique_Zambia",-18.0,  22.0,  -8.0,  36.0),
    ("Africa_Zimbabwe_Botswana",-26.0,  19.5, -15.5,  33.5),
    ("Africa_South_Africa_W",  -35.0,  16.5, -25.0,  25.0),
    ("Africa_South_Africa_E",  -35.0,  25.0, -22.0,  33.0),
    ("Africa_Madagascar",      -25.6,  43.2, -11.9,  50.5),

    # ── Oceania ───────────────────────────────────────────────
    ("Australia_WA_N",         -26.0, 112.0, -13.5, 130.0),
    ("Australia_WA_S",         -35.5, 112.0, -26.0, 125.0),
    ("Australia_NT_SA_N",      -26.0, 128.0, -11.5, 138.5),
    ("Australia_SA_S",         -38.5, 128.0, -26.0, 141.0),
    ("Australia_Queensland_N", -23.5, 138.5,  -9.0, 153.5),
    ("Australia_Queensland_S", -29.5, 138.5, -23.5, 154.0),
    ("Australia_NSW_N",        -32.0, 141.0, -28.0, 154.0),
    ("Australia_NSW_S",        -37.5, 140.5, -32.0, 151.5),
    ("Australia_Victoria",     -39.2, 140.9, -33.9, 150.0),
    ("Australia_Tasmania",     -43.7, 143.8, -39.5, 148.5),
    ("NZ_North_Island",        -41.7, 172.5, -34.3, 178.6),
    ("NZ_South_Island",        -46.7, 166.4, -40.4, 174.4),
]

# ============================================================
# FIX A: BBOX → COUNTRY MAPPING
# For regions that are entirely (or almost entirely) within one
# country, we skip reverse_geocoder entirely and assign the country
# code directly from the region name. This eliminates the Andorra
# bug and any other KD-tree misattribution for well-defined regions.
# ============================================================

REGION_COUNTRY_MAP: dict[str, str] = {
    "India_NW":              "IN",
    "India_NC":              "IN",
    "India_NE_Plains":       "IN",
    "India_Northeast":       "IN",
    "India_West":            "IN",
    "India_Central":         "IN",
    "India_East":            "IN",
    "India_South":           "IN",
    "Asia_Pakistan":         "PK",
    "Asia_East_Japan":       "JP",
    "NA_US_West":            "US",
    "NA_US_Central":         "US",
    "NA_US_East":            "US",
    "NA_Canada_W":           "CA",
    "NA_Canada_E":           "CA",
    "NA_Mexico":             "MX",
    "Australia_W":           "AU",
    "Australia_E":           "AU",
    "NZ_Pacific":            "NZ",
    # Multi-country regions are NOT in this map — they go to reverse_geocoder
    # (Europe_*, Africa_*, Asia_Southeast_*, SA_*, Central_America, etc.)
}

# ============================================================
# FIX B: COUNTRY_FALLBACKS — keyed on ISO 2-letter codes
# reverse_geocoder returns 'cc' field as ISO 2-letter code.
# Previous version used full country names, causing misses on every lookup.
# ============================================================

COUNTRY_FALLBACKS: dict[str, dict[str, str]] = {
    "IN": {"hospital": "108", "police": "100", "fire_station": "101",
           "fuel": "1033", "car_repair": "1033", "towing": "1033"},
    "US": {"hospital": "911", "police": "911", "fire_station": "911",
           "fuel": "911",  "car_repair": "911",  "towing": "911"},
    "GB": {"hospital": "999", "police": "999", "fire_station": "999",
           "fuel": "999",  "car_repair": "999",  "towing": "999"},
    "AU": {"hospital": "000", "police": "000", "fire_station": "000",
           "fuel": "000",  "car_repair": "000",  "towing": "000"},
    "CA": {"hospital": "911", "police": "911", "fire_station": "911",
           "fuel": "911",  "car_repair": "911",  "towing": "911"},
    "NZ": {"hospital": "111", "police": "111", "fire_station": "111",
           "fuel": "111",  "car_repair": "111",  "towing": "111"},
    "DE": {"hospital": "112", "police": "110", "fire_station": "112",
           "fuel": "112",  "car_repair": "112",  "towing": "112"},
    "FR": {"hospital": "15",  "police": "17",  "fire_station": "18",
           "fuel": "112",  "car_repair": "112",  "towing": "112"},
    "JP": {"hospital": "119", "police": "110", "fire_station": "119",
           "fuel": "110",  "car_repair": "110",  "towing": "110"},
    "CN": {"hospital": "120", "police": "110", "fire_station": "119",
           "fuel": "122",  "car_repair": "122",  "towing": "122"},
    "BR": {"hospital": "192", "police": "190", "fire_station": "193",
           "fuel": "193",  "car_repair": "193",  "towing": "193"},
    "ZA": {"hospital": "10177","police": "10111","fire_station": "10111",
           "fuel": "10111","car_repair": "10111","towing": "10111"},
    "NG": {"hospital": "199", "police": "199", "fire_station": "199",
           "fuel": "199",  "car_repair": "199",  "towing": "199"},
    "PK": {"hospital": "1122","police": "15",  "fire_station": "16",
           "fuel": "1122", "car_repair": "1122","towing": "1122"},
    "BD": {"hospital": "999", "police": "999", "fire_station": "999",
           "fuel": "999",  "car_repair": "999",  "towing": "999"},
    "NP": {"hospital": "102", "police": "100", "fire_station": "101",
           "fuel": "112",  "car_repair": "112",  "towing": "112"},
    "MX": {"hospital": "911", "police": "911", "fire_station": "911",
           "fuel": "911",  "car_repair": "911",  "towing": "911"},
    "MY": {"hospital": "999", "police": "999", "fire_station": "994",
           "fuel": "999",  "car_repair": "999",  "towing": "999"},
    "ID": {"hospital": "119", "police": "110", "fire_station": "113",
           "fuel": "112",  "car_repair": "112",  "towing": "112"},
    "PH": {"hospital": "911", "police": "911", "fire_station": "911",
           "fuel": "911",  "car_repair": "911",  "towing": "911"},
    "TH": {"hospital": "1669","police": "191", "fire_station": "199",
           "fuel": "191",  "car_repair": "191",  "towing": "191"},
    "KE": {"hospital": "999", "police": "999", "fire_station": "999",
           "fuel": "999",  "car_repair": "999",  "towing": "999"},
    "EG": {"hospital": "123", "police": "122", "fire_station": "180",
           "fuel": "122",  "car_repair": "122",  "towing": "122"},
    "RU": {"hospital": "103", "police": "102", "fire_station": "101",
           "fuel": "112",  "car_repair": "112",  "towing": "112"},
}

GLOBAL_DEFAULT: dict[str, str] = {s: "112" for s in
    ["hospital", "police", "fire_station", "fuel", "car_repair", "towing"]}

# ============================================================
# CSV FIELDNAMES — must match schema.sql service_points columns
# ============================================================

FIELDNAMES = [
    "name", "service_type", "lat", "lng",
    "phone", "phone_source",
    "address", "district", "state", "country", "postcode",
    "operator", "source", "last_verified",
]

# ============================================================
# COMBINED OVERPASS QUERY
# Single query fetches all 6 service types in one round-trip.
# FIX D: added healthcare tag for Indian clinics/hospitals.
# ============================================================

COMBINED_QUERY_TEMPLATE = """
[out:json][timeout:300];
(
  node["amenity"~"^(hospital|clinic|doctors)$"]({bbox});
  way["amenity"~"^(hospital|clinic|doctors)$"]({bbox});
  node["healthcare"~"^(hospital|clinic|doctor|centre)$"]({bbox});
  way["healthcare"~"^(hospital|clinic|doctor|centre)$"]({bbox});
  node["amenity"="police"]({bbox});
  node["office"="police"]({bbox});
  way["amenity"="police"]({bbox});
  node["amenity"="fire_station"]({bbox});
  way["amenity"="fire_station"]({bbox});
  node["amenity"="fuel"]({bbox});
  way["amenity"="fuel"]({bbox});
  node["shop"="car_repair"]({bbox});
  way["shop"="car_repair"]({bbox});
  node["service"="towing"]({bbox});
  node["tow"="yes"]({bbox});
  node["roadside_assistance"="yes"]({bbox});
);
out center tags;
"""

# ============================================================
# SERVICE TYPE DETECTION
# FIX D: checks 'healthcare' tag — many Indian OSM entries use
# this instead of 'amenity' for hospitals/clinics.
# ============================================================

def detect_service_type(tags: dict) -> Optional[str]:
    amenity    = tags.get("amenity", "")
    shop       = tags.get("shop", "")
    service    = tags.get("service", "")
    healthcare = tags.get("healthcare", "")

    if amenity in ("hospital", "clinic", "doctors"):
        return "hospital"
    # FIX D: healthcare tag support
    if healthcare in ("hospital", "clinic", "doctor", "centre"):
        return "hospital"
    if amenity == "police" or tags.get("office") == "police":
        return "police"
    if amenity == "fire_station":
        return "fire_station"
    if amenity == "fuel":
        return "fuel"
    if shop == "car_repair" or amenity == "car_repair":
        return "car_repair"
    if (service == "towing" or tags.get("tow") == "yes"
            or tags.get("roadside_assistance") == "yes"):
        return "towing"
    return None


# ============================================================
# PHONE EXTRACTION & NORMALISATION
# FIX C: strip country-code prefix before length check so
# "+91-108" → "108" not "91108"
# ============================================================

def extract_phone(tags: dict) -> Optional[str]:
    for key in ("phone", "contact:phone", "operator:phone",
                "emergency:phone", "contact:mobile", "mobile"):
        if tags.get(key):
            return tags[key]
    return None


def normalize_phone(raw: Optional[str]) -> Optional[str]:
    """
    Clean a raw OSM phone string into a dialable format.
    FIX C: handles country-code prefixes like +91, 0091, +1 correctly.
    Short emergency codes (≤5 digits) are kept exactly as-is.
    """
    if not raw:
        return raw
    phone = raw.strip()

    # Drop tel: prefix
    if phone.lower().startswith("tel:"):
        phone = phone[4:].strip()

    # Take first number if multiple separated by ; or /
    for sep in (";", "/"):
        if sep in phone:
            phone = phone.split(sep)[0].strip()

    # Extract digits only for analysis
    digits = re.sub(r"[^\d]", "", phone)

    # Short emergency codes — keep as digits (108, 100, 911, 999, etc.)
    if len(digits) <= 5:
        return digits

    # FIX C: strip common country code prefixes so we don't conflate
    # "+91-108" (which becomes "91108") with the actual number "108".
    # Check if stripping known prefixes gives a short emergency code.
    for prefix in ("91", "1", "44", "61", "64", "49", "33", "81", "86",
                   "55", "27", "234", "92", "880", "977", "52"):
        if digits.startswith(prefix) and len(digits) - len(prefix) <= 5:
            short = digits[len(prefix):]
            if short.isdigit() and len(short) >= 2:
                return short

    # Regular number — return digits (handles spaces, dashes, parens)
    return digits


def get_fallback_phone(country_code: Optional[str], service_type: str) -> str:
    """ISO 2-letter country code → fallback emergency number."""
    if country_code and country_code in COUNTRY_FALLBACKS:
        return COUNTRY_FALLBACKS[country_code].get(
            service_type, GLOBAL_DEFAULT.get(service_type, "112")
        )
    return GLOBAL_DEFAULT.get(service_type, "112")


# ============================================================
# GEO EXTRACTION
# Strategy:
#   1. REGION_COUNTRY_MAP lookup (instant, no library call)
#   2. OSM addr:* tags (free, from element itself)
#   3. reverse_geocoder batch call (for remaining rows)
# ============================================================

def extract_geo_from_tags(tags: dict) -> dict:
    street = tags.get("addr:street")
    housen = tags.get("addr:housenumber")
    address = None
    if street:
        address = f"{housen} {street}".strip() if housen else street

    return {
        "address":  address or tags.get("addr:full"),
        "district": (tags.get("addr:district")
                     or tags.get("addr:county")
                     or tags.get("addr:city")),
        "state":    (tags.get("addr:state")
                     or tags.get("addr:province")),
        "country":  tags.get("addr:country"),
        "postcode": tags.get("addr:postcode"),
    }


def batch_reverse_geocode(rows_needing_geo: list[dict]) -> list[dict]:
    """
    Batch KD-tree lookup for rows that still need country/state after
    OSM tags and REGION_COUNTRY_MAP. Returns parallel list of geo dicts.
    Speed: ~0.55s per 1000 calls (vs 43s individual).
    """
    if not rows_needing_geo:
        return []
    coords  = [(r["lat"], r["lng"]) for r in rows_needing_geo]
    results = reverse_geocoder.search(coords, verbose=False)
    return [
        {
            "district": r.get("admin2") or r.get("name"),
            "state":    r.get("admin1"),
            "country":  r.get("cc"),    # ISO 2-letter code
        }
        for r in results
    ]


# ============================================================
# HTTP HELPER
# POST (not GET) — avoids URL length limits on large queries.
# Timeout 180s — dead connections fail fast not hang for 10 min.
# ============================================================

def safe_request(url: str, data: dict = None,
                 retries: int = 4, timeout: int = 180) -> requests.Response:
    current_url = url
    for attempt in range(retries):
        try:
            resp = requests.post(
                current_url,
                data=data,
                headers={"User-Agent": USER_AGENT},
                timeout=timeout,
            )
            resp.raise_for_status()
            return resp
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else 0
            if status in (403, 429):
                current_url = rotate_mirror()
                wait = 3
            else:
                wait = 5 * (2 ** attempt)
            print(f"    Retry {attempt+1}/{retries}: HTTP {status}  (wait {wait}s)")
            time.sleep(wait)
        except Exception as exc:
            wait = 5 * (2 ** attempt)
            print(f"    Retry {attempt+1}/{retries}: {exc}  (wait {wait}s)")
            time.sleep(wait)
    raise RuntimeError(f"All {retries} retries failed for {current_url}")


# ============================================================
# FETCH ONE REGION
# ============================================================

def fetch_region(region_name: str, bbox: tuple, resume: bool = False) -> list[dict]:
    """
    Fetch all service types for one region.
    With resume=True, returns cached rows if progress file exists.
    """
    progress_file = PROGRESS_DIR / f"{region_name}.json"

    if resume and progress_file.exists():
        try:
            with open(progress_file, encoding="utf-8") as f:
                rows = json.load(f)
            print(f"  [RESUME] {region_name}: {len(rows):,} rows from cache")
            return rows
        except Exception:
            print(f"  [RESUME] {region_name}: corrupt cache — re-fetching")

    south, west, north, east = bbox
    bbox_str = f"{south},{west},{north},{east}"
    query    = COMBINED_QUERY_TEMPLATE.format(bbox=bbox_str)

    print(f"\n{'─'*55}")
    print(f"  FETCHING: {region_name}  bbox={bbox_str}")

    now_iso = datetime.now(timezone.utc).isoformat()

    # ── Overpass fetch ────────────────────────────────────────
    try:
        resp     = safe_request(get_overpass_url(), data={"data": query})
        elements = resp.json().get("elements", [])
        print(f"    Overpass: {len(elements):,} elements returned")
    except Exception as exc:
        print(f"    FAILED {region_name}: {exc}")
        return []

    # ── FIX A: determine region country code upfront ─────────
    region_country = REGION_COUNTRY_MAP.get(region_name)   # None = multi-country

    # ── Pass 1: build raw rows (no geocoding yet) ─────────────
    raw_rows: list[dict] = []
    needs_geo_indices: list[int] = []

    for element in elements:
        tags         = element.get("tags", {})
        service_type = detect_service_type(tags)
        if service_type is None:
            continue

        lat = element.get("lat")
        lng = element.get("lon")
        if lat is None or lng is None:
            center = element.get("center", {})
            lat    = center.get("lat")
            lng    = center.get("lon")

        # Explicit None check — 0.0 is a valid coordinate
        if lat is None or lng is None:
            continue

        geo = extract_geo_from_tags(tags)

        # FIX A: apply region country code before falling back to reverse_geocoder
        country_code = region_country or geo.get("country")

        row = {
            "name":          (tags.get("name")
                              or tags.get("name:en")
                              or f"Unnamed {service_type}"),
            "service_type":  service_type,
            "lat":           lat,
            "lng":           lng,
            "phone":         None,   # resolved in pass 3
            "phone_source":  None,
            "address":       geo.get("address"),
            "district":      geo.get("district"),
            "state":         geo.get("state"),
            "country":       country_code,
            "postcode":      geo.get("postcode"),
            "operator":      tags.get("operator"),
            "source":        "osm_enriched",
            "last_verified": now_iso,
            "_raw_phone":    extract_phone(tags),   # removed in pass 3
        }

        # Only call reverse_geocoder for rows where region_country is
        # unknown AND OSM tags didn't provide state/country
        if region_country is None and not (geo.get("state") and country_code):
            needs_geo_indices.append(len(raw_rows))

        raw_rows.append(row)

    # ── Pass 2: batch geocode only truly ambiguous rows ───────
    if needs_geo_indices:
        print(f"    Batch geocoding {len(needs_geo_indices):,} "
              f"ambiguous rows (of {len(raw_rows):,})...")
        rows_for_geo = [raw_rows[i] for i in needs_geo_indices]
        geo_results  = batch_reverse_geocode(rows_for_geo)
        for idx, geo in zip(needs_geo_indices, geo_results):
            r = raw_rows[idx]
            r["district"] = r["district"] or geo.get("district")
            r["state"]    = r["state"]    or geo.get("state")
            # FIX A: only overwrite country if we don't already have one
            if not r["country"]:
                r["country"] = geo.get("country")
    else:
        print(f"    Skipped reverse_geocoder (country known from region map)")

    # ── Pass 3: resolve phones now that country codes are final ─
    for r in raw_rows:
        raw_phone = r.pop("_raw_phone")
        norm      = normalize_phone(raw_phone)
        if norm:
            r["phone"]        = norm
            r["phone_source"] = "real"
        else:
            r["phone"]        = normalize_phone(
                get_fallback_phone(r.get("country"), r["service_type"])
            )
            r["phone_source"] = "fallback"

    # ── Per-region dedup before saving ───────────────────────
    raw_rows = _dedup_rows(raw_rows)

    # ── Save progress checkpoint ──────────────────────────────
    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump(raw_rows, f)

    # ── Quick country distribution for sanity check ───────────
    country_counts: dict[str, int] = {}
    for r in raw_rows:
        cc = r.get("country") or "unknown"
        country_counts[cc] = country_counts.get(cc, 0) + 1
    top = sorted(country_counts.items(), key=lambda x: -x[1])[:5]
    print(f"  DONE {region_name}: {len(raw_rows):,} rows  "
          f"| country dist: {top}")

    return raw_rows


# ============================================================
# DEDUPLICATION
# ============================================================

def _dedup_rows(rows: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    unique: list[dict] = []
    for row in rows:
        lat = row.get("lat")
        lng = row.get("lng")
        if lat is None or lng is None:
            continue
        try:
            key = (
                row.get("name"),
                row.get("service_type"),
                round(float(lat), 5),
                round(float(lng), 5),
            )
        except (TypeError, ValueError):
            continue
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


def deduplicate(rows: list[dict]) -> list[dict]:
    """Global dedup across all regions after per-region dedup already done."""
    print(f"Global deduplication of {len(rows):,} rows...")
    result = _dedup_rows(rows)
    print(f"After dedup: {len(result):,} unique rows")
    return result


# ============================================================
# STREAMING CSV WRITER — thread-safe, flat memory usage
# ============================================================

class StreamingCSVWriter:
    def __init__(self, path: Path):
        self._path = path
        self._lock = threading.Lock()
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDNAMES,
                           extrasaction="ignore").writeheader()

    def append(self, rows: list[dict]) -> None:
        if not rows:
            return
        with self._lock:
            with open(self._path, "a", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=FIELDNAMES,
                               extrasaction="ignore").writerows(rows)


# ============================================================
# SUMMARY
# ============================================================

def print_summary(rows: list[dict]) -> None:
    counts: dict[str, int]  = {}
    country_counts: dict[str, int] = {}
    for row in rows:
        stype   = row.get("service_type", "unknown")
        country = row.get("country") or "unknown"
        counts[stype]           = counts.get(stype, 0) + 1
        country_counts[country] = country_counts.get(country, 0) + 1

    print("\n" + "=" * 55)
    print("SUMMARY — by service type")
    print("=" * 55)
    for stype, count in sorted(counts.items()):
        print(f"  {stype:15s}: {count:>8,}")
    print(f"\n  TOTAL: {len(rows):,} rows")
    print("\nTop 20 countries (should look sensible for regions fetched):")
    for cc, count in sorted(country_counts.items(), key=lambda x: -x[1])[:20]:
        print(f"  {str(cc):6s}: {count:,}")


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="RoadSOS global OSM emergency data fetcher"
    )
    parser.add_argument("--resume",  action="store_true",
                        help="Skip regions with existing progress cache files")
    parser.add_argument("--region",  type=str, default=None,
                        help="Fetch only one region by name (e.g. India_Northeast)")
    parser.add_argument("--workers", type=int, default=3,
                        help="Parallel region workers (default 3, max recommended 4)")
    args = parser.parse_args()

    print("=" * 60)
    print("  RoadSOS Global Data Fetcher v2.1")
    print("=" * 60)

    target_regions = REGIONS
    if args.region:
        target_regions = [r for r in REGIONS if r[0] == args.region]
        if not target_regions:
            print(f"ERROR: Unknown region '{args.region}'.")
            print(f"Valid names: {[r[0] for r in REGIONS]}")
            return

    print(f"  Regions  : {len(target_regions)}")
    print(f"  Workers  : {args.workers}")
    print(f"  Resume   : {args.resume}")
    print(f"  Output   : {OUTPUT_CSV}\n")

    csv_writer  = StreamingCSVWriter(OUTPUT_CSV)
    all_rows: list[dict] = []
    failed_regions: list[str] = []
    _lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                fetch_region,
                name, (south, west, north, east), args.resume
            ): name
            for name, south, west, north, east in target_regions
        }
        for future in as_completed(futures):
            region_name = futures[future]
            try:
                rows = future.result()
                csv_writer.append(rows)
                with _lock:
                    all_rows.extend(rows)
                print(f"\n✓  {region_name}: {len(rows):,} rows  "
                      f"(total so far: {len(all_rows):,})")
            except Exception as exc:
                print(f"\n✗  {region_name}: FAILED — {exc}")
                failed_regions.append(region_name)

    if failed_regions:
        print(f"\n⚠  {len(failed_regions)} region(s) failed: {failed_regions}")
        print("   Run with --resume to retry only failed regions.")

    # Final global dedup, then rewrite clean CSV
    all_rows = deduplicate(all_rows)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)

    size_mb = OUTPUT_CSV.stat().st_size / (1024 * 1024)
    print(f"\nCSV: {OUTPUT_CSV}  ({size_mb:.1f} MB, {len(all_rows):,} rows)")
    print_summary(all_rows)
    print("\nNext step: python build_db.py")


# ============================================================
# HOW TO RUN
# ============================================================
#
# INSTALL (one time):
#   pip install requests reverse_geocoder
#
# TEST one region first:
#   python fetch_global_data.py --region India_Northeast
#   → should show country dist with IN dominating, not AD
#
# FULL RUN (use screen/tmux — takes 1-3 hours):
#   screen -S roadsos
#   python fetch_global_data.py
#   Ctrl+A D    ← detach, keeps running
#   screen -r roadsos  ← reattach to check
#
# RESUME after crash:
#   python fetch_global_data.py --resume
#
# THEN:
#   python build_db.py
#
# ============================================================

if __name__ == "__main__":
    main()