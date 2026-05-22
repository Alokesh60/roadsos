from app.db.sqlite_db import get_connection

conn = get_connection()

cursor = conn.cursor()

columns = [

    ("city", "TEXT"),
    ("state", "TEXT"),
    ("country", "TEXT"),
    ("rating", "REAL DEFAULT 0"),
    ("availability", "BOOLEAN DEFAULT 1"),
    ("verified", "BOOLEAN DEFAULT 0"),
    ("source", "TEXT DEFAULT 'sqlite'"),
    ("emergency_score", "REAL DEFAULT 0")
]

for column_name, column_type in columns:

    try:

        cursor.execute(
            f"""
            ALTER TABLE emergency_services
            ADD COLUMN {column_name} {column_type}
            """
        )

        print(f"Added column: {column_name}")

    except Exception as e:

        print(f"Skipped {column_name}: {e}")

conn.commit()

conn.close()

print("Migration completed.")