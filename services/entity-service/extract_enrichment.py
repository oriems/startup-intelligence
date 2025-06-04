import os
import psycopg2
import re
import openai
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

DB_PARAMS = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "dbname": os.getenv("POSTGRES_DB", "startup_intel"),
    "user": os.getenv("POSTGRES_USER", "startup"),
    "password": os.getenv("POSTGRES_PASSWORD", "secret"),
    "port": os.getenv("POSTGRES_PORT", 5432)
}

def extract_with_regex(text):
    amount_match = re.search(r"(\$|USD|€|EUR|£|GBP)?\s?(\d+[,.]?\d*[Mm]?)", text)
    round_match = re.search(r"(Series\s?[A-D]|Seed|Pre-Seed|Growth)", text, re.IGNORECASE)

    return {
        "round_amount": amount_match.group(2) if amount_match else None,
        "currency": amount_match.group(1).strip() if amount_match and amount_match.group(1) else "USD",
        "round_type": round_match.group(1) if round_match else None
    }

def extract_with_openai(text):
    prompt = f"""
You are a financial data extraction assistant. Extract the following fields from this tweet:
- company_name
- round_amount
- currency
- round_type
- date (mentioned in text, else use today's date)
- investors (as a list)
- location (if mentioned)

Tweet: "{text}"

Return as JSON.
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        return eval(response.choices[0].message["content"])
    except Exception as e:
        return {"notes": f"Failed to parse response: {e}"}

def process_tweets():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    cur.execute("SELECT tweet_id, tweet_text, created_at FROM twitter_raw WHERE tweet_id NOT IN (SELECT tweet_id FROM twitter_processed);")
    rows = cur.fetchall()

    for tweet_id, text, created_at in rows:
        base = extract_with_regex(text)

        # Use OpenAI only if regex finds a likely match
        if base["round_type"] or base["round_amount"]:
            enriched = extract_with_openai(text)
        else:
            enriched = {}

        final = {
            **base,
            **enriched,
            "tweet_id": tweet_id,
            "date": enriched.get("date") or created_at,
            "source_url": f"https://twitter.com/i/web/status/{tweet_id}"
        }

        cur.execute("""
        INSERT INTO twitter_processed (
            tweet_id, company_name, round_amount, currency, round_type,
            date, investors, location, source_url, confidence, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [
            final.get("tweet_id"),
            final.get("company_name"),
            final.get("round_amount"),
            final.get("currency"),
            final.get("round_type"),
            final.get("date"),
            final.get("investors"),
            final.get("location"),
            final.get("source_url"),
            final.get("confidence"),
            final.get("notes")
        ])

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    process_tweets()
