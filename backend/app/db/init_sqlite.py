from app.db.sqlite_db import get_connection

conn = get_connection()

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS emergency_services (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    type TEXT NOT NULL,

    latitude REAL NOT NULL,

    longitude REAL NOT NULL,

    phone TEXT,

    address TEXT,

    city TEXT,

    state TEXT,

    country TEXT,

    rating REAL DEFAULT 0,

    availability BOOLEAN DEFAULT 1,

    verified BOOLEAN DEFAULT 0,

    source TEXT DEFAULT 'sqlite',

    emergency_score REAL DEFAULT 0
)
""")

conn.commit()

conn.close()

print("SQLite database initialized.")