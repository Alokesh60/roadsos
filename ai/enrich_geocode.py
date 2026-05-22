import sqlite3, requests, time

DB_PATH = "ai/roadsos.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


rows = cursor.execute("""
    SELECT id, latitude, longitude FROM facilities
    WHERE city = 'Unknown' OR state = 'Unknown'
""").fetchall()

print(f"Rows to enrich: {len(rows)}")

for i, (fid, lat, lon) in enumerate(rows):
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": "RoadSoS-Enrichment/1.0"},
            timeout=10
        )
        data = r.json()
        addr = data.get("address", {})
        city = addr.get("city") or addr.get("town") or addr.get("village") or "Unknown"
        state = addr.get("state", "Unknown")
        address = data.get("display_name", "Unknown")

        cursor.execute("""
            UPDATE facilities SET city=?, state=?, address=? WHERE id=?
        """, (city, state, address, fid))

        if i % 100 == 0:
            conn.commit()
            print(f"Progress: {i}/{len(rows)}")

        time.sleep(1.1)  # Nominatim rate limit: 1 req/sec

    except Exception as e:
        print(f"Error on id={fid}: {e}")
        time.sleep(2)

conn.commit()
conn.close()
print("Done.")