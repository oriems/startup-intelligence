import psycopg2

DB_PARAMS = {
    "host": "localhost",
    "dbname": "startup_intel",
    "user": "startup",
    "password": "secret",
    "port": 5432
}

N = 10  # Number of most recent rows to delete

conn = psycopg2.connect(**DB_PARAMS)
cur = conn.cursor()

cur.execute(f"""
    DELETE FROM twitter_processed
    WHERE tweet_id IN (
        SELECT tweet_id FROM twitter_processed
        ORDER BY date DESC
        LIMIT %s
    );
""", (N,))

conn.commit()
cur.close()
conn.close()