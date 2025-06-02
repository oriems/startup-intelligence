import time
import psycopg2

conn = psycopg2.connect(
    dbname="startup_intel",
    user="startup",
    password="secret",
    host="postgres"
)
cur = conn.cursor()
print("Entity processor service started...")

while True:
    cur.execute("SELECT id, name FROM startups WHERE description IS NULL LIMIT 1;")
    row = cur.fetchone()
    if row:
        startup_id, name = row
        enriched_description = f"{name} is a seed-stage startup revolutionizing X."

        cur.execute("""
            UPDATE startups
            SET description = %s
            WHERE id = %s;
        """, (enriched_description, startup_id))
        conn.commit()
        print(f"Enriched: {name}")
    time.sleep(10)
