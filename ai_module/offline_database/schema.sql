-- ============================================================
-- RoadSOS Offline Database Schema (Unified Architecture)
-- Version: 2026-05
-- ============================================================
-- PURPOSE:
--   Global offline emergency fallback DB for RoadSOS.
--   Uses ONE unified service_points table instead of separate
--   hospitals / police / fuel / fire / towing tables.
--
-- Android Room @Entity field names MUST match column names exactly.
-- Any rename requires a Room migration.
--
-- FIXES APPLIED (2026-05):
--   #1  nh_corridors: added UNIQUE(nh_number, segment_name, state)
--       to prevent duplicate rows on re-seed.
--   #2  chatbot_intents: added UNIQUE(intent) to prevent duplicate
--       intent rows on re-seed.
--   #3  offline_alert_queue: added ON DELETE CASCADE on sos_event_id
--       so deleting a sos_event cleans up its queued alerts.
--   #4  keywords column renamed to keywords_json with
--       CHECK(json_valid(keywords_json)) to catch malformed JSON
--       at insert time. (Matches build_db.py column name.)
-- ============================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;


-- ============================================================
-- 1. DB VERSION
-- ============================================================

CREATE TABLE IF NOT EXISTS db_version (
    id          INTEGER PRIMARY KEY CHECK (id = 1),
    version     TEXT    NOT NULL,
    seeded_at   TEXT    NOT NULL
);


-- ============================================================
-- 2. UNIFIED SERVICE POINTS
-- ============================================================
-- Replaces old separate hospitals / police_stations tables.
-- Query example:
--   SELECT * FROM service_points
--   WHERE service_type = 'hospital'
--   ORDER BY (lat - ?) * (lat - ?) + (lng - ?) * (lng - ?)
--   LIMIT 5;
-- (Android Room uses Haversine or a spatial library for real distance.)
-- ============================================================

CREATE TABLE IF NOT EXISTS service_points (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,

    name            TEXT    NOT NULL,

    service_type    TEXT    NOT NULL CHECK (
        service_type IN (
            'hospital',
            'police',
            'fire_station',
            'fuel',
            'car_repair',
            'towing'
        )
    ),

    lat             REAL    NOT NULL,
    lng             REAL    NOT NULL,

    phone           TEXT,

    phone_source    TEXT    DEFAULT 'unavailable' CHECK (
        phone_source IN ('real', 'fallback', 'unavailable')
    ),

    address         TEXT,
    district        TEXT,
    state           TEXT,
    country         TEXT,
    postcode        TEXT,

    operator        TEXT,

    source          TEXT    DEFAULT 'osm',

    last_verified   TEXT    DEFAULT CURRENT_TIMESTAMP,

    updated_at      TEXT    DEFAULT CURRENT_TIMESTAMP,

    -- Prevent exact duplicates on re-seed
    UNIQUE(name, service_type, lat, lng)
);

CREATE INDEX IF NOT EXISTS idx_sp_service_type
    ON service_points(service_type);

CREATE INDEX IF NOT EXISTS idx_sp_country
    ON service_points(country);

CREATE INDEX IF NOT EXISTS idx_sp_state
    ON service_points(state);

CREATE INDEX IF NOT EXISTS idx_sp_district
    ON service_points(district);

CREATE INDEX IF NOT EXISTS idx_sp_lat_lng
    ON service_points(lat, lng);

-- Composite index used by the common "find nearest X" query
CREATE INDEX IF NOT EXISTS idx_sp_type_lat_lng
    ON service_points(service_type, lat, lng);


-- ============================================================
-- 3. EMERGENCY NUMBERS
-- ============================================================
-- Tiered fallback:
--   Tier 1 = Global default (country IS NULL)
--   Tier 2 = Country-level
--   Tier 3 = State/District-level
-- ============================================================

CREATE TABLE IF NOT EXISTS emergency_numbers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,

    category    TEXT    NOT NULL CHECK (
        category IN (
            'ambulance', 'police', 'fire',
            'highway', 'disaster', 'unified', 'towing'
        )
    ),

    number      TEXT    NOT NULL,

    tier        INTEGER NOT NULL CHECK (tier IN (1, 2, 3)),

    country     TEXT,
    state       TEXT,
    district    TEXT,

    label       TEXT
);

CREATE INDEX IF NOT EXISTS idx_en_cat_tier
    ON emergency_numbers(category, tier);

CREATE INDEX IF NOT EXISTS idx_en_country
    ON emergency_numbers(country);

CREATE INDEX IF NOT EXISTS idx_en_state
    ON emergency_numbers(state);


-- ============================================================
-- PRE-SEEDED EMERGENCY NUMBERS
-- ============================================================

-- Global tier-1 defaults (no country — always available)
INSERT OR IGNORE INTO emergency_numbers
    (category, number, tier, country, label)
VALUES
    ('ambulance', '112', 1, NULL, 'Global Unified Emergency'),
    ('police',    '112', 1, NULL, 'Global Unified Emergency'),
    ('fire',      '112', 1, NULL, 'Global Unified Emergency'),
    ('unified',   '112', 1, NULL, 'Global Unified Emergency'),
    ('highway',   '1033', 1, 'India', 'NHAI Road Helpline'),
    ('towing',    '1033', 1, 'India', 'Roadside Assistance');

-- India country-level (tier 2)
INSERT OR IGNORE INTO emergency_numbers
    (category, number, tier, country, state, label)
VALUES
    ('ambulance', '108', 2, 'India', NULL, 'India Ambulance (EMRI)'),
    ('ambulance', '102', 2, 'India', NULL, 'India State Ambulance'),
    ('police',    '100', 2, 'India', NULL, 'India Police'),
    ('fire',      '101', 2, 'India', NULL, 'India Fire Brigade'),
    ('unified',   '112', 2, 'India', NULL, 'India Unified Emergency');

-- USA (tier 2)
INSERT OR IGNORE INTO emergency_numbers
    (category, number, tier, country, label)
VALUES
    ('ambulance', '911', 2, 'United States', 'US Emergency'),
    ('police',    '911', 2, 'United States', 'US Emergency'),
    ('fire',      '911', 2, 'United States', 'US Emergency'),
    ('unified',   '911', 2, 'United States', 'US Emergency');

-- UK (tier 2)
INSERT OR IGNORE INTO emergency_numbers
    (category, number, tier, country, label)
VALUES
    ('ambulance', '999', 2, 'United Kingdom', 'UK Emergency'),
    ('police',    '999', 2, 'United Kingdom', 'UK Emergency'),
    ('fire',      '999', 2, 'United Kingdom', 'UK Emergency'),
    ('unified',   '999', 2, 'United Kingdom', 'UK Emergency');

-- Germany / EU representative (tier 2)
INSERT OR IGNORE INTO emergency_numbers
    (category, number, tier, country, label)
VALUES
    ('ambulance', '112', 2, 'Germany', 'EU Emergency'),
    ('police',    '112', 2, 'Germany', 'EU Emergency'),
    ('fire',      '112', 2, 'Germany', 'EU Emergency'),
    ('unified',   '112', 2, 'Germany', 'EU Emergency');


-- ============================================================
-- 4. CHATBOT INTENTS
-- ============================================================
-- FIX #4: renamed 'keywords' → 'keywords_json' (matches build_db.py)
-- FIX #2: UNIQUE(intent) prevents duplicate rows on re-seed
-- ============================================================

CREATE TABLE IF NOT EXISTS chatbot_intents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,

    intent          TEXT    NOT NULL UNIQUE,           -- FIX #2

    -- FIX #4: was `keywords TEXT NOT NULL`
    -- JSON-validated; build_db.py stores json.dumps([...]) here
    keywords_json   TEXT    CHECK(json_valid(keywords_json)),

    response_en     TEXT    NOT NULL,
    response_hi     TEXT,
    response_as     TEXT,

    action_label    TEXT,
    action_number   TEXT
);

CREATE INDEX IF NOT EXISTS idx_intent
    ON chatbot_intents(intent);


-- ============================================================
-- 5. NH CORRIDORS
-- ============================================================
-- FIX #1: UNIQUE(nh_number, segment_name, state) prevents duplicates
-- on re-seed runs.
-- ============================================================

CREATE TABLE IF NOT EXISTS nh_corridors (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,

    nh_number       TEXT    NOT NULL,
    segment_name    TEXT,
    helpline        TEXT,
    state           TEXT,

    lat_start       REAL,
    lng_start       REAL,
    lat_end         REAL,
    lng_end         REAL,

    -- FIX #1: was missing UNIQUE constraint
    UNIQUE(nh_number, segment_name, state)
);

CREATE INDEX IF NOT EXISTS idx_nh_number
    ON nh_corridors(nh_number);


-- ============================================================
-- 6. SOS EVENTS
-- ============================================================
-- Stores offline SOS history; synced when internet returns.
-- ============================================================

CREATE TABLE IF NOT EXISTS sos_events (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,

    lat                 REAL    NOT NULL,
    lng                 REAL    NOT NULL,

    intent              TEXT,
    service_type        TEXT,
    resolved_number     TEXT,

    status              TEXT    DEFAULT 'pending' CHECK (
        status IN ('pending', 'synced', 'failed')
    ),

    created_at          TEXT    DEFAULT CURRENT_TIMESTAMP,
    synced_at           TEXT
);

CREATE INDEX IF NOT EXISTS idx_sos_status
    ON sos_events(status);


-- ============================================================
-- 7. RESPONDER CACHE
-- ============================================================
-- Caches recent Google Places results for offline use.
-- TTL (10 min or 300 m movement) must be enforced in app logic —
-- there is no expiry column here because Android handles it via
-- cached_at comparison in the repository layer.
-- ============================================================

CREATE TABLE IF NOT EXISTS responder_cache (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,

    place_id        TEXT    NOT NULL UNIQUE,

    name            TEXT    NOT NULL,
    service_type    TEXT    NOT NULL,

    lat             REAL    NOT NULL,
    lng             REAL    NOT NULL,

    phone           TEXT,
    address         TEXT,

    cached_at       TEXT    DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cache_service_type
    ON responder_cache(service_type);


-- ============================================================
-- 8. OFFLINE ALERT QUEUE
-- ============================================================
-- Unsent SOS payloads; retried when internet returns.
-- FIX #3: ON DELETE CASCADE on sos_event_id prevents orphan rows
-- when a sos_event is deleted.
-- ============================================================

CREATE TABLE IF NOT EXISTS offline_alert_queue (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,

    -- FIX #3: was just REFERENCES without ON DELETE CASCADE
    sos_event_id    INTEGER REFERENCES sos_events(id) ON DELETE CASCADE,

    payload_json    TEXT    NOT NULL,

    attempts        INTEGER DEFAULT 0,
    last_attempt    TEXT,

    created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 9. CACHED SERVICES
-- ============================================================
-- Stores last successful GET /emergency-data response for
-- version-check bootstrapping when fully offline.
-- ============================================================

CREATE TABLE IF NOT EXISTS cached_services (
    id              INTEGER PRIMARY KEY CHECK (id = 1),

    payload_json    TEXT    NOT NULL,

    fetched_at      TEXT    DEFAULT CURRENT_TIMESTAMP
);