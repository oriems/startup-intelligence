from dotenv import load_dotenv
from pathlib import Path
import os
import psycopg2

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("DB_HOST")
)
cur = conn.cursor()

# Create startups table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS startups (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    website TEXT,
    description TEXT
);
""")

# Create twitter_raw table for storing raw tweet data
cur.execute("""
CREATE TABLE twitter_raw (
    tweet_id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ,
    tweet_text TEXT,
    author_id TEXT,
    lang TEXT,
    source TEXT,
    is_round_event BOOLEAN
);

""")

conn.commit()
print("✅ Tables 'startups' and 'twitter_raw' ensured.")
cur.close()
conn.close()
