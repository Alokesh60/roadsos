import sqlite3
import os


# =====================================
# DATABASE PATH
# =====================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../"
    )
)

DB_PATH = os.path.join(
    BASE_DIR,
    "roadsos.db"
)


# =====================================
# GET CONNECTION
# =====================================

def get_connection():

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


# =====================================
# INITIALIZE DATABASE
# =====================================

def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    # =================================
    # SERVICE POINTS
    # =================================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS service_points (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        service_type TEXT,

        latitude REAL,

        longitude REAL,

        phone TEXT,

        phone_source TEXT,

        address TEXT,

        district TEXT,

        state TEXT,

        country TEXT,

        postcode TEXT,

        operator TEXT,

        source TEXT,

        last_verified TEXT

    )

    """)

    # =================================
    # CACHED LIVE SERVICES
    # =================================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS cached_services (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        service_type TEXT,

        latitude REAL,

        longitude REAL,

        phone TEXT,

        address TEXT,

        city TEXT,

        state TEXT,

        country TEXT,

        source TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    # =================================
    # SOS EVENTS
    # =================================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS sos_events (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id TEXT,

        emergency_type TEXT,

        latitude REAL,

        longitude REAL,

        message TEXT,

        source TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    # =================================
    # OFFLINE ALERT QUEUE
    # =================================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS offline_alert_queue (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        phone TEXT,

        message TEXT,

        status TEXT DEFAULT 'PENDING',

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    # =================================
    # RESPONDER CACHE
    # =================================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS responder_cache (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id TEXT,

        latitude REAL,

        longitude REAL,

        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    # =================================
    # EMERGENCY NUMBERS
    # =================================

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS emergency_numbers (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        country TEXT,

        service_type TEXT,

        emergency_number TEXT

    )

    """)

    conn.commit()

    conn.close()

    print(
        "[SQLite] Database initialized."
    )