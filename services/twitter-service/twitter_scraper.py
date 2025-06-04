import requests
import psycopg2
from dotenv import load_dotenv
from pathlib import Path
import os
from datetime import datetime, timedelta, timezone
import re

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

SEARCH_QUERY = (
    "(raised OR announced OR closed) "
    "(funding OR seed OR \"series a\" OR \"series b\") "
    "(startup OR company OR platform) "
    "-is:retweet lang:en"
)
TWITTER_URL = "https://api.twitter.com/2/tweets/search/recent"

def create_headers():
    return {"Authorization": f"Bearer {os.getenv('TWITTER_BEARER_TOKEN')}"}

# fifteen_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=15)
# start_time = fifteen_minutes_ago.isoformat()

def get_tweets():
    params = {
        "query": SEARCH_QUERY,
        "tweet.fields": "created_at,text,author_id,lang,source",
        # "start_time": start_time,
        "max_results": 10  # increase for better coverage
    }
    response = requests.get(TWITTER_URL, headers=create_headers(), params=params)
    response.raise_for_status()
    return response.json().get("data", [])

def is_funding_related(tweet_text: str) -> bool:
    if len(tweet_text) < 120:
        return False
    return bool(re.search(r'(series\s?[ABCD]|seed|raised|closed|funding)', tweet_text, re.IGNORECASE))


def insert_raw_tweets(tweets):
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("DB_HOST")
    )
    cur = conn.cursor()
    for tweet in tweets:
        tweet_id = tweet["id"]
        text = tweet["text"]
        is_round_event = is_funding_related(text)

        try:
            cur.execute("""
                INSERT INTO twitter_raw (tweet_id, created_at, tweet_text, author_id, lang, source, is_round_event)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (tweet_id) DO NOTHING;
            """, (
                tweet_id,
                tweet["created_at"],
                text,
                tweet.get("author_id"),
                tweet.get("lang"),
                tweet.get("source"),
                is_round_event
            ))
            print(f"✅ Inserted tweet {tweet_id}")
        except Exception as e:
            print(f"❌ Error inserting tweet {tweet_id}:", e)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    tweets = get_tweets()
    insert_raw_tweets(tweets)
