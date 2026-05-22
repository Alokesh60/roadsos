from sqlite_db import get_connection

conn = get_connection()

cursor = conn.cursor()

cursor.execute("DELETE FROM emergency_services")

conn.commit()

conn.close()

print("Old services deleted.")