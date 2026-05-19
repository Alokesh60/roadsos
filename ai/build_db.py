"""
RoadSoS — Emergency Facilities Database Builder
================================================
Uses OSM Overpass API (free, no key needed).
Run: python build_db.py

Output: roadsos.db (SQLite) — ready for scorer.py and chroma_setup.py
"""

import sqlite3
import time
import requests
import re
import sys
from datetime import date

# ── Config ────────────────────────────────────────────────────────────────────

OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

DB_PATH = "roadsos.db"
TODAY = date.today().isoformat()

STATIC_AMBULANCE = {
    "Guwahati":    {"name": "Assam 108 Ambulance", "phone": "108"},
    "Delhi":       {"name": "Delhi Emergency Ambulance", "phone": "102"},
    "Mumbai":      {"name": "Mumbai 108 Ambulance", "phone": "108"},
    "Bengaluru":   {"name": "Karnataka 108 Ambulance", "phone": "108"},
    "Chennai":     {"name": "Tamil Nadu 108 Ambulance", "phone": "108"},
    "Kolkata":     {"name": "West Bengal 102 Ambulance", "phone": "102"},
    "Hyderabad":   {"name": "Telangana 108 Ambulance", "phone": "108"},
    "Pune":        {"name": "Maharashtra 108 Ambulance", "phone": "108"},
    "Jaipur":      {"name": "Rajasthan 108 Ambulance", "phone": "108"},
    "Ahmedabad":   {"name": "Gujarat 108 Ambulance", "phone": "108"},
    "London":      {"name": "NHS Ambulance Service", "phone": "999"},
    "New York":    {"name": "NYC EMS Ambulance", "phone": "911"},
}

HEADERS = {
    "User-Agent": "RoadSoS-HackathonApp/1.0 (road safety emergency services research)",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
}

CITIES = [
    ("Guwahati",    26.1445, 91.7362,  15000),
    ("Delhi",       28.6139, 77.2090,  20000),
    ("Mumbai",      19.0760, 72.8777,  20000),
    ("Bengaluru",   12.9716, 77.5946,  20000),
    ("Chennai",     13.0827, 80.2707,  20000),
    ("Kolkata",     22.5726, 88.3639,  18000),
    ("Hyderabad",   17.3850, 78.4867,  20000),
    ("Pune",        18.5204, 73.8567,  18000),
    ("Jaipur",      26.9124, 75.7873,  15000),
    ("Ahmedabad",   23.0225, 72.5714,  18000),
    ("London",      51.5074, -0.1278,  15000),
    ("New York",    40.7128, -74.0060, 15000),
]

FACILITY_QUERIES = [
    {
        "facility_type": "hospital",
        "tags": ['["amenity"="hospital"]', '["amenity"="clinic"]'],
        "default_services": "emergency trauma care general medicine surgery",
    },
    {
        "facility_type": "ambulance",
        "tags": ['["emergency"="ambulance_station"]'],
        "default_services": "ambulance emergency medical response",
    },
    {
        "facility_type": "police",
        "tags": ['["amenity"="police"]'],
        "default_services": "police emergency law enforcement accident response",
    },
    {
        "facility_type": "towing",
        "tags": ['["shop"="car_repair"]', '["amenity"="vehicle_inspection"]'],
        "default_services": "vehicle towing roadside assistance breakdown recovery",
    },
    {
        "facility_type": "puncture",
        "tags": ['["shop"="tyres"]'],
        "default_services": "tyre puncture repair wheel alignment",
    },
]

# ── Mirror management ──────────────────────────────────────────────────────────

_current_mirror_index = 0

def get_mirror():
    return OVERPASS_MIRRORS[_current_mirror_index % len(OVERPASS_MIRRORS)]

def rotate_mirror():
    global _current_mirror_index
    _current_mirror_index += 1
    new = get_mirror()
    print(f"    ↪ Switching to mirror: {new}")
    return new

# ── Database setup ─────────────────────────────────────────────────────────────

def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS facilities (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            name              TEXT NOT NULL,
            facility_type     TEXT NOT NULL,
            latitude          REAL NOT NULL,
            longitude         REAL NOT NULL,
            phone             TEXT,
            address           TEXT,
            country           TEXT DEFAULT 'India',
            rating            REAL,
            response_time_min INTEGER,
            is_available      INTEGER DEFAULT 1,
            services_offered  TEXT,
            last_verified     TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_latlon ON facilities(latitude, longitude)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON facilities(facility_type)")
    conn.commit()
    print("✓ Database initialised")

# ── OSM Overpass query ─────────────────────────────────────────────────────────

def fetch_osm(lat, lon, radius, tag, facility_type):
    query = f"""
[out:json][timeout:60][maxsize:1073741824];
(
  node{tag}(around:{radius},{lat},{lon});
  way{tag}(around:{radius},{lat},{lon});
);
out center tags;
"""

    for retry in range(2):
        for attempt in range(len(OVERPASS_MIRRORS)):
            url = get_mirror()
            try:
                resp = requests.post(
                    url,
                    data={"data": query},
                    headers=HEADERS,
                    timeout=60
                )

                if resp.status_code == 406:
                    print(f"    ⚠ 406 from {url} — rotating mirror")
                    rotate_mirror()
                    continue

                if resp.status_code == 429:
                    print(f"    ⚠ Rate limited — waiting 15s")
                    time.sleep(15)
                    continue

                resp.raise_for_status()
                return resp.json().get("elements", [])

            except requests.exceptions.Timeout:
                print(f"    ⚠ Timeout — rotating mirror")
                rotate_mirror()

            except Exception as e:
                print(f"    ⚠ Error: {e} — rotating mirror")
                rotate_mirror()

        wait = 2 ** retry
        print(f"    ↻ Waiting {wait}s before retry...")
        time.sleep(wait)

    print(f"    ✗ All mirrors failed for {facility_type} {tag}")
    return []

# ── Element → row ──────────────────────────────────────────────────────────────

def _clean_phone(raw):
    if not raw:
        return None
    cleaned = re.sub(r"[^\d\+\s\-]", "", str(raw)).strip()
    return cleaned if cleaned else None

def _infer_country(lat, lon):
    if 6.0 <= lat <= 37.5 and 68.0 <= lon <= 97.5:
        return "India"
    if 49.0 <= lat <= 61.0 and -8.0 <= lon <= 2.0:
        return "UK"
    if 24.0 <= lat <= 50.0 and -125.0 <= lon <= -66.0:
        return "USA"
    return "Unknown"

def _infer_response_time(facility_type):
    return {
        "hospital": 15,
        "ambulance": 10,
        "police": 12,
        "towing": 30,
        "puncture": 20
    }.get(facility_type, 15)

def inject_static_ambulance(city_name, lat, lon):
    data = STATIC_AMBULANCE.get(city_name)
    if not data:
        return None

    return {
        "name": data["name"],
        "facility_type": "ambulance",
        "latitude": lat,
        "longitude": lon,
        "phone": data["phone"],
        "address": city_name,
        "country": _infer_country(lat, lon),
        "rating": None,
        "response_time_min": 10,
        "is_available": 1,
        "services_offered": "ambulance emergency medical response",
        "last_verified": TODAY,
    }

def element_to_row(el, facility_type, default_services):
    tags = el.get("tags", {})

    if el["type"] == "node":
        lat, lon = el.get("lat"), el.get("lon")
    else:
        center = el.get("center", {})
        lat, lon = center.get("lat"), center.get("lon")

    if lat is None or lon is None:
        return None

    name = (
        tags.get("name:en") or
        tags.get("name") or
        tags.get("operator") or
        f"Emergency {facility_type.title()}"
    )

    addr_parts = [
        tags.get("addr:housenumber", ""),
        tags.get("addr:street", ""),
        tags.get("addr:suburb", ""),
        tags.get("addr:city", ""),
        tags.get("addr:state", ""),
    ]

    address = ", ".join(p for p in addr_parts if p).strip(", ") or None
    phone = _clean_phone(tags.get("phone") or tags.get("contact:phone") or tags.get("contact:mobile"))
    services = tags.get("description") or tags.get("service") or default_services
    country = _infer_country(lat, lon)

    return {
        "name": name,
        "facility_type": facility_type,
        "latitude": lat,
        "longitude": lon,
        "phone": phone,
        "address": address,
        "country": country,
        "rating": None,
        "response_time_min": _infer_response_time(facility_type),
        "is_available": 1,
        "services_offered": services,
        "last_verified": TODAY,
    }

# ── Deduplication ──────────────────────────────────────────────────────────────

def deduplicate(rows):
    seen = set()
    unique = []

    for row in rows:
        key = (
            row["name"].lower().strip(),
            round(row["latitude"], 4),
            round(row["longitude"], 4)
        )
        if key not in seen:
            seen.add(key)
            unique.append(row)

    return unique

# ── Main collection loop ───────────────────────────────────────────────────────

def collect_all():
    all_rows = []

    for city_name, lat, lon, radius in CITIES:
        print(f"\n{'─'*55}")
        print(f"  {city_name}  ({lat}, {lon})")
        print(f"{'─'*55}")

        city_rows = []
        ambulance_count = 0

        for fq in FACILITY_QUERIES:
            ftype = fq["facility_type"]
            services = fq["default_services"]

            for tag in fq["tags"]:
                print(f"  → {ftype:12s}  {tag}")
                elements = fetch_osm(lat, lon, radius, tag, ftype)

                count = 0
                for el in elements:
                    row = element_to_row(el, ftype, services)
                    if row:
                        city_rows.append(row)
                        count += 1
                        if ftype == "ambulance":
                            ambulance_count += 1

                print(f"     {count} rows parsed")
                time.sleep(1.5)

        if ambulance_count == 0:
            print("  ⚠ No ambulance nodes found — injecting fallback")
            fallback = inject_static_ambulance(city_name, lat, lon)
            if fallback:
                city_rows.append(fallback)

        city_rows = deduplicate(city_rows)
        print(f"\n  ✓ {city_name}: {len(city_rows)} unique facilities")
        all_rows.extend(city_rows)

    return all_rows

# ── Insert to SQLite ───────────────────────────────────────────────────────────

def insert_rows(conn, rows):
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO facilities
            (name, facility_type, latitude, longitude, phone, address,
             country, rating, response_time_min, is_available,
             services_offered, last_verified)
        VALUES
            (:name, :facility_type, :latitude, :longitude, :phone, :address,
             :country, :rating, :response_time_min, :is_available,
             :services_offered, :last_verified)
    """, rows)
    conn.commit()
    return cursor.rowcount

# ── Coverage report ────────────────────────────────────────────────────────────

def print_report(conn):
    print("\n" + "═"*55)
    print("  DATABASE SUMMARY")
    print("═"*55)

    total = conn.execute("SELECT COUNT(*) FROM facilities").fetchone()[0]
    print(f"  Total facilities : {total}")

    print("\n  By type:")
    for row in conn.execute(
        "SELECT facility_type, COUNT(*) FROM facilities GROUP BY facility_type ORDER BY COUNT(*) DESC"
    ):
        print(f"    {row[0]:15s} {row[1]}")

    print("\n  By country:")
    for row in conn.execute(
        "SELECT country, COUNT(*) FROM facilities GROUP BY country ORDER BY COUNT(*) DESC"
    ):
        print(f"    {row[0]:15s} {row[1]}")

    print("\n  Phone coverage:")
    with_phone = conn.execute(
        "SELECT COUNT(*) FROM facilities WHERE phone IS NOT NULL"
    ).fetchone()[0]

    pct = (100 * with_phone // total) if total else 0
    print(f"    {with_phone}/{total} entries have phone numbers ({pct}%)")

    print("═"*55)
    print(f"\n  Saved to: {DB_PATH}")
    print("  Ready for scorer.py and chroma_setup.py\n")

# ── Quick connectivity test ────────────────────────────────────────────────────

def test_connection():
    print("  Testing Overpass connectivity...")
    test_query = "[out:json][timeout:10]; node['amenity'='hospital'](around:1000,26.1445,91.7362); out 1;"

    for i, mirror in enumerate(OVERPASS_MIRRORS):
        try:
            resp = requests.post(
                mirror,
                data={"data": test_query},
                headers=HEADERS,
                timeout=15
            )

            if resp.status_code == 200:
                print(f"  ✓ Connected via {mirror}\n")
                global _current_mirror_index
                _current_mirror_index = i
                return True
            else:
                print(f"  ✗ {mirror} → HTTP {resp.status_code}")

        except Exception as e:
            print(f"  ✗ {mirror} → {e}")

    return False

# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    print("\n🚑  RoadSoS DB Builder — OSM Overpass Edition")
    print(f"    Target cities : {len(CITIES)}")
    print(f"    Output        : {DB_PATH}\n")

    if not test_connection():
        print("\n✗ No Overpass mirror reachable. Check your internet connection.")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    rows = collect_all()

    if not rows:
        print("\n⚠ No rows collected.")
        conn.close()
        sys.exit(1)

    print(f"\n\n  Deduplicating {len(rows)} total rows...")
    rows = deduplicate(rows)
    print(f"  {len(rows)} unique rows after global deduplication")

    print(f"  Inserting into {DB_PATH}...")
    inserted = insert_rows(conn, rows)
    print(f"  ✓ {inserted} rows inserted")

    print_report(conn)
    conn.close()

if __name__ == "__main__":
    main()