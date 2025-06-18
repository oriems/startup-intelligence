import time
import psycopg2
from llm_enrich import enrich_startup_description
import os
host = os.getenv("DB_HOST", "localhost")  # default to localhost


conn = psycopg2.connect(
    dbname="startup_intel",
    user="startup",
    password="secret",
    host=host
)
cur = conn.cursor()
print("LLM Enrichment Scheduler started...")

while True:
    cur.execute("SELECT id, name, website FROM startups WHERE description IS NULL LIMIT 1;")
    row = cur.fetchone()
    if row:
        startup_id, name, website = row
        description = enrich_startup_description(name, website)

        cur.execute("""
            UPDATE startups SET description = %s WHERE id = %s;
        """, (description, startup_id))
        conn.commit()
        print(f"Enriched {name}: {description}")
    time.sleep(15)
