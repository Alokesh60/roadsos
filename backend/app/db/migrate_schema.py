from sqlite_db import get_connection

conn = get_connection()

cursor = conn.cursor()

# Add missing columns safely

try:
    cursor.execute("""
        ALTER TABLE emergency_services
        ADD COLUMN country TEXT DEFAULT 'India'
    """)
except:
    pass

try:
    cursor.execute("""
        ALTER TABLE emergency_services
        ADD COLUMN city TEXT
    """)
except:
    pass

try:
    cursor.execute("""
        ALTER TABLE emergency_services
        ADD COLUMN state TEXT
    """)
except:
    pass

try:
    cursor.execute("""
        ALTER TABLE emergency_services
        ADD COLUMN rating REAL
    """)
except:
    pass

try:
    cursor.execute("""
        ALTER TABLE emergency_services
        ADD COLUMN response_time_min INTEGER
    """)
except:
    pass

try:
    cursor.execute("""
        ALTER TABLE emergency_services
        ADD COLUMN is_available INTEGER DEFAULT 1
    """)
except:
    pass

try:
    cursor.execute("""
        ALTER TABLE emergency_services
        ADD COLUMN services_offered TEXT
    """)
except:
    pass

try:
    cursor.execute("""
        ALTER TABLE emergency_services
        ADD COLUMN last_verified TEXT
    """)
except:
    pass

try:

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS emergency_logs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        message TEXT,

        detected_type TEXT,

        priority TEXT,

        confidence REAL,

        country TEXT,

        classification_status TEXT,

        recommended_service TEXT,

        created_at TEXT

    )

    """)

except:
    pass

conn.commit()

conn.close()

print("Database schema migration completed.")