"""
build_db.py
-----------
Reads the output of fetch_global_data.py and builds:
  1. roadsos.db          — SQLite database shipped in the Android APK assets
  2. emergency_seed.json — served by the backend GET /emergency-data endpoint

Run AFTER fetch_global_data.py has completed.

USAGE:
    python build_db.py

    # Override the DB version string (useful for CI/CD):
    ROADSOS_DB_VERSION=2026-05-custom python build_db.py

DEPENDENCIES:
    None (stdlib only)

EXPECTED RUNTIME:
    ~2-5 minutes for a full global dataset.
    Progress is printed continuously so you know it's not frozen.
"""

import csv
import json
import os
import shutil
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

# Auto-generated from current month. Override with env var for CI/CD.
# This fixes the old manual DB_VERSION = "2026-05" which someone
# would inevitably forget to update.
DB_VERSION = os.environ.get(
    "ROADSOS_DB_VERSION",
    datetime.now().strftime("%Y-%m"),
)

BASE_DIR    = Path(__file__).parent
DATA_DIR    = BASE_DIR / "data"
SCHEMA_FILE = BASE_DIR / "schema.sql"

DB_OUTPUT = BASE_DIR / "roadsos.db"
DB_TEMP   = BASE_DIR / "roadsos_temp.db"   # atomic: build here, rename after success

JSON_OUTPUT = BASE_DIR / "emergency_seed.json"

# Warn if service_points count seems unrealistically low
MIN_EXPECTED_SERVICE_POINTS = 10_000


# ============================================================
# HELPERS
# ============================================================

def _ts() -> str:
    """Current time string for progress output."""
    return datetime.now().strftime("%H:%M:%S")


def _log(msg: str) -> None:
    print(f"[{_ts()}] {msg}")


def _read_csv(filename: str) -> list[dict]:
    path = DATA_DIR / filename
    if not path.exists():
        _log(f"WARNING: {filename} not found — skipping.")
        return []
    with open(path, encoding="utf-8") as f:
        rows = [
            {k: (v.strip() if v and v.strip() != "" else None) for k, v in row.items()}
            for row in csv.DictReader(f)
        ]
    _log(f"  Read {len(rows):,} rows from {filename}")
    return rows


def _to_float(val) -> float | None:
    try:
        return float(val) if val is not None else None
    except (ValueError, TypeError):
        return None


def _to_int(val) -> int | None:
    try:
        return int(val) if val is not None else None
    except (ValueError, TypeError):
        return None


def _validate_coords(lat, lng) -> bool:
    """
    Explicit None checks — lat/lng == 0.0 is a valid coordinate
    (equator / prime meridian) but evaluates falsy.
    Old pattern `if lat and lng` would silently skip those rows.
    """
    if lat is None or lng is None:
        return False
    if not (-90.0 <= lat <= 90.0):
        return False
    if not (-180.0 <= lng <= 180.0):
        return False
    return True


# ============================================================
# BUILD SQLITE
# ============================================================

def build_sqlite() -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """
    Build roadsos.db via roadsos_temp.db, then atomically rename.
    A crash mid-build does NOT destroy the previous good DB.

    Returns (valid_service_points, emergency_rows, corridors, intents)
    so build_json_seed() can reuse them without re-reading CSVs.
    """
    _log(f"Building SQLite → {DB_OUTPUT}")
    t0 = time.time()

    # Clean up any leftover temp from a previous failed build
    if DB_TEMP.exists():
        DB_TEMP.unlink()
        _log("  Removed stale temp DB from previous failed run.")

    conn = sqlite3.connect(str(DB_TEMP))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # ── Apply schema ─────────────────────────────────────────
    _log("  Applying schema...")
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(
            f"schema.sql not found at {SCHEMA_FILE}. "
            "Make sure schema.sql is in the same directory as build_db.py."
        )
    with open(SCHEMA_FILE, encoding="utf-8") as f:
        cur.executescript(f.read())
    _log("  Schema applied.")

    # ── db_version ───────────────────────────────────────────
    now_iso = datetime.now(timezone.utc).isoformat()
    cur.execute(
        "INSERT OR REPLACE INTO db_version (id, version, seeded_at) VALUES (1, ?, ?)",
        (DB_VERSION, now_iso),
    )
    _log(f"  DB version: {DB_VERSION}")

    # ── service_points ───────────────────────────────────────
    _log("  Inserting service_points...")
    raw_rows = _read_csv("service_points.csv")

    inserted = 0
    skipped  = 0
    valid_service_points: list[dict] = []

    for row in raw_rows:
        lat = _to_float(row.get("lat"))
        lng = _to_float(row.get("lng"))

        if not _validate_coords(lat, lng):
            skipped += 1
            continue

        try:
            cur.execute(
                """
                INSERT OR IGNORE INTO service_points
                  (name, service_type, lat, lng, phone, phone_source,
                   address, district, state, country, postcode,
                   operator, source, last_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("name"),
                    row.get("service_type"),
                    lat, lng,
                    row.get("phone"),
                    row.get("phone_source"),
                    row.get("address"),
                    row.get("district"),
                    row.get("state"),
                    row.get("country"),
                    row.get("postcode"),
                    row.get("operator"),
                    row.get("source"),
                    row.get("last_verified"),
                ),
            )
            inserted += 1
            valid_service_points.append({**row, "lat": lat, "lng": lng})
        except Exception as exc:
            _log(f"  Skipped bad row: {exc}")
            skipped += 1

    _log(f"  service_points: {inserted:,} inserted, {skipped:,} skipped")

    # Warn if the count seems suspiciously low — likely fetch_global_data
    # failed silently or the CSV is from an incomplete run
    if inserted < MIN_EXPECTED_SERVICE_POINTS:
        _log(
            f"  ⚠ WARNING: Only {inserted:,} service_points inserted. "
            f"Expected at least {MIN_EXPECTED_SERVICE_POINTS:,}. "
            "Did fetch_global_data.py complete fully?"
        )

    # ── emergency_numbers ────────────────────────────────────
    _log("  Inserting emergency_numbers from CSV...")
    emergency_rows = _read_csv("emergency_numbers.csv")
    for row in emergency_rows:
        cur.execute(
            """
            INSERT OR IGNORE INTO emergency_numbers
              (category, number, tier, country, state, district, label)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row.get("category"),
                row.get("number"),
                _to_int(row.get("tier")),
                row.get("country"),
                row.get("state"),
                row.get("district"),
                row.get("label"),
            ),
        )
    _log(f"  emergency_numbers: {len(emergency_rows):,} CSV rows processed "
         f"(schema pre-seeds global defaults separately)")

    # ── nh_corridors ─────────────────────────────────────────
    _log("  Inserting nh_corridors...")
    corridors = _read_csv("nh_corridors.csv")
    for row in corridors:
        cur.execute(
            """
            INSERT OR IGNORE INTO nh_corridors
              (nh_number, segment_name, helpline, state,
               lat_start, lng_start, lat_end, lng_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row.get("nh_number"),
                row.get("segment_name"),
                row.get("helpline"),
                row.get("state"),
                _to_float(row.get("lat_start")),
                _to_float(row.get("lng_start")),
                _to_float(row.get("lat_end")),
                _to_float(row.get("lng_end")),
            ),
        )
    _log(f"  nh_corridors: {len(corridors):,} rows")

    # ── chatbot_intents ──────────────────────────────────────
    _log("  Inserting chatbot_intents...")
    intents_path = DATA_DIR / "chatbot_intents.json"
    intents: list[dict] = []
    if intents_path.exists():
        with open(intents_path, encoding="utf-8") as f:
            intents = json.load(f)
        for item in intents:
            cur.execute(
                """
                INSERT OR IGNORE INTO chatbot_intents
                  (intent, keywords_json, response_en, response_hi, response_as,
                   action_label, action_number)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.get("intent"),
                    json.dumps(item.get("keywords", []), ensure_ascii=False),
                    item.get("response_en"),
                    item.get("response_hi"),
                    item.get("response_as"),
                    item.get("action_label"),
                    item.get("action_number"),
                ),
            )
        _log(f"  chatbot_intents: {len(intents):,} rows")
    else:
        _log("  WARNING: chatbot_intents.json not found — chatbot offline fallback "
             "will not work.")

    conn.commit()
    conn.close()

    # ── Atomic rename ─────────────────────────────────────────
    # Only replaces the live DB after a fully successful build.
    # A crash anywhere above leaves roadsos.db untouched.
    shutil.move(str(DB_TEMP), str(DB_OUTPUT))
    size_kb = DB_OUTPUT.stat().st_size / 1024
    elapsed = time.time() - t0
    _log(f"  SQLite DB ready: {DB_OUTPUT}  ({size_kb:,.1f} KB, {elapsed:.1f}s)")

    return valid_service_points, emergency_rows, corridors, intents


# ============================================================
# BUILD JSON SEED
# ============================================================

def build_json_seed(
    valid_service_points: list[dict],
    emergency_rows: list[dict],
    corridors: list[dict],
    intents: list[dict],
) -> None:
    """
    Build emergency_seed.json served by GET /emergency-data.

    Shape (new unified architecture):
    {
      "version": "...",
      "generated_at": "...",
      "service_points": [...],
      "emergency_numbers": [...],
      "chatbot_intents": [...],
      "nh_corridors": [...]
    }

    Uses the same validated rows that build_sqlite() already filtered —
    SQLite and JSON will always be in sync.
    """
    _log(f"Building JSON seed → {JSON_OUTPUT}")
    t0 = time.time()

    emergency_numbers = [
        {
            "category": r.get("category"),
            "number":   r.get("number"),
            "tier":     _to_int(r.get("tier")),
            "country":  r.get("country"),
            "state":    r.get("state"),
            "district": r.get("district"),
            "label":    r.get("label"),
        }
        for r in emergency_rows
    ]

    valid_corridors = [
        {
            "nh_number":    r.get("nh_number"),
            "segment_name": r.get("segment_name"),
            "helpline":     r.get("helpline"),
            "state":        r.get("state"),
            "lat_start":    _to_float(r.get("lat_start")),
            "lng_start":    _to_float(r.get("lng_start")),
            "lat_end":      _to_float(r.get("lat_end")),
            "lng_end":      _to_float(r.get("lng_end")),
        }
        for r in corridors
    ]

    seed = {
        "version":          DB_VERSION,
        "generated_at":     datetime.now(timezone.utc).isoformat(),
        "service_points":   valid_service_points,
        "emergency_numbers": emergency_numbers,
        "chatbot_intents":  intents,
        "nh_corridors":     valid_corridors,
    }

    with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(seed, f, ensure_ascii=False, indent=2)

    size_kb = JSON_OUTPUT.stat().st_size / 1024
    elapsed = time.time() - t0
    _log(f"  JSON ready: {JSON_OUTPUT}  ({size_kb:,.1f} KB, {elapsed:.1f}s)")
    _log(f"  service_points:    {len(valid_service_points):,}")
    _log(f"  emergency_numbers: {len(emergency_numbers):,}")
    _log(f"  chatbot_intents:   {len(intents):,}")
    _log(f"  nh_corridors:      {len(valid_corridors):,}")


# ============================================================
# VERIFY DATABASE
# ============================================================

def verify_db() -> bool:
    """
    Quick sanity check on the built DB.
    Returns True if all required tables have data.
    Prints a table of row counts.
    """
    _log(f"Verifying {DB_OUTPUT}...")

    # These tables are allowed to start empty (runtime-populated by Android)
    empty_ok = {
        "db_version",
        "sos_events",
        "responder_cache",
        "offline_alert_queue",
        "cached_services",
    }

    tables = [
        "service_points",
        "emergency_numbers",
        "chatbot_intents",
        "nh_corridors",
        "db_version",
        "sos_events",
        "responder_cache",
        "offline_alert_queue",
        "cached_services",
    ]

    conn = sqlite3.connect(str(DB_OUTPUT))
    cur  = conn.cursor()
    all_ok = True

    print()
    print(f"  {'Table':30s}  {'Rows':>8}  Status")
    print(f"  {'─' * 30}  {'─' * 8}  {'─' * 6}")

    for table in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            ok     = count > 0 or table in empty_ok
            status = "OK" if ok else "⚠ EMPTY"
            print(f"  {table:30s}  {count:>8,}  {status}")
            if not ok:
                all_ok = False
        except Exception as exc:
            print(f"  {table:30s}  {'ERROR':>8}  {exc}")
            all_ok = False

    cur.execute("SELECT version, seeded_at FROM db_version")
    row = cur.fetchone()
    if row:
        print(f"\n  Version:    {row[0]}")
        print(f"  Seeded at:  {row[1]}")

    conn.close()
    print()

    if all_ok:
        _log("Verification passed — all tables OK.")
    else:
        _log("Verification FAILED — some required tables are empty. "
             "Check the warnings above.")
    return all_ok


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    print("=" * 60)
    print(f"RoadSOS Offline DB Builder  |  version {DB_VERSION}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    t_total = time.time()

    valid_service_points, emergency_rows, corridors, intents = build_sqlite()
    build_json_seed(valid_service_points, emergency_rows, corridors, intents)
    ok = verify_db()

    elapsed = time.time() - t_total
    print("=" * 60)
    _log(f"Build complete in {elapsed:.1f}s")
    print()
    print("Files to ship in Android APK  /assets/ folder:")
    print(f"  {DB_OUTPUT}")
    print()
    print("File served by backend GET /emergency-data:")
    print(f"  {JSON_OUTPUT}")
    print()
    if not ok:
        print("⚠  WARNING: Verification failed. Do not ship this build.")
    print("=" * 60)


# ============================================================
# ============================================================
# HOW TO RUN — READ THIS BEFORE STARTING
# ============================================================
# ============================================================
#
# PREREQUISITES
# -------------
#   - Python 3.10+
#   - fetch_global_data.py must have completed successfully
#   - The following files must exist in data/:
#       data/service_points.csv       ← from fetch_global_data.py
#       data/emergency_numbers.csv    ← manual / maintained by you
#       data/nh_corridors.csv         ← manual / maintained by you
#       data/chatbot_intents.json     ← manual / maintained by you
#   - schema.sql must be in the same directory as this file
#   - No pip installs needed (stdlib only)
#
# COMMAND
# -------
#   python build_db.py
#
#   # With a custom version string:
#   ROADSOS_DB_VERSION=2026-05-rc1 python build_db.py
#
# EXPECTED RUNTIME
# ----------------
#   ~2-5 minutes for a full global dataset (~3M service points).
#   Progress is logged with timestamps so you can see it's running.
#
# WHERE TO RUN
# ------------
#   Run this wherever fetch_global_data.py ran (same machine /
#   server), then copy the output files:
#     roadsos.db          → Android project /app/src/main/assets/
#     emergency_seed.json → your backend server, served at GET /emergency-data
#
# OUTPUT
# ------
#   roadsos.db            ← ship in Android APK
#   emergency_seed.json   ← serve from backend
#
# AFTER THIS COMPLETES
# --------------------
#   1. Copy roadsos.db into your Android project:
#        app/src/main/assets/roadsos.db
#
#   2. Copy emergency_seed.json to your backend server.
#      Backend should serve it at:
#        GET /emergency-data
#
#   3. Run your test suite:
#        pytest tests/ -v
#
# ============================================================


if __name__ == "__main__":
    main()