-- =====================================
-- GLOBAL UNIFIED SERVICE POINTS
-- =====================================

CREATE TABLE IF NOT EXISTS service_points (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    service_type TEXT NOT NULL,

    phone TEXT,

    phone_source TEXT,

    address TEXT,

    district TEXT,

    state TEXT,

    country TEXT,

    postcode TEXT,

    latitude REAL NOT NULL,

    longitude REAL NOT NULL,

    operator TEXT,

    source TEXT,

    last_verified TEXT
);


-- =====================================
-- EMERGENCY NUMBERS
-- =====================================

CREATE TABLE IF NOT EXISTS emergency_numbers (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    country TEXT,

    service_type TEXT,

    emergency_number TEXT
);


-- =====================================
-- CHATBOT INTENTS
-- =====================================

CREATE TABLE IF NOT EXISTS chatbot_intents (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    intent TEXT,

    keywords TEXT,

    response TEXT
);


-- =====================================
-- HIGHWAY CORRIDORS
-- =====================================

CREATE TABLE IF NOT EXISTS nh_corridors (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    highway_name TEXT,

    state TEXT,

    risk_level TEXT
);


-- =====================================
-- SOS EVENTS
-- =====================================

CREATE TABLE IF NOT EXISTS sos_events (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id TEXT,

    message TEXT,

    detected_type TEXT,

    latitude REAL,

    longitude REAL,

    priority TEXT,

    created_at TEXT
);


-- =====================================
-- RESPONDER CACHE
-- =====================================

CREATE TABLE IF NOT EXISTS responder_cache (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id TEXT,

    latitude REAL,

    longitude REAL,

    fcm_token TEXT,

    is_online INTEGER DEFAULT 1,

    updated_at TEXT
);


-- =====================================
-- OFFLINE ALERT QUEUE
-- =====================================

CREATE TABLE IF NOT EXISTS offline_alert_queue (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    alert_type TEXT,

    payload TEXT,

    retry_count INTEGER DEFAULT 0,

    created_at TEXT
);


-- =====================================
-- CACHED SERVICES
-- =====================================

CREATE TABLE IF NOT EXISTS cached_services (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT,

    service_type TEXT,

    latitude REAL,

    longitude REAL,

    source TEXT,

    cached_at TEXT
);


-- =====================================
-- DATABASE VERSION
-- =====================================

CREATE TABLE IF NOT EXISTS db_version (

    version TEXT
);