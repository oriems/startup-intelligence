import time
import psycopg2
import os
host = os.getenv("DB_HOST", "localhost")  # default to localhost

conn = psycopg2.connect(
    dbname="startup_intel",
    user="startup",
    password="secret",
    host=host
)

cur = conn.cursor()
print("Scraper service started...")

while True:
    startup_name = "CoolStartup"
    url = "https://example.com"
    print("Inserting startup into DB...")

    cur.execute("""
        INSERT INTO startups (name, website)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING;
    """, (startup_name, url))

    conn.commit()
    time.sleep(30)
