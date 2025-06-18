import os
import psycopg2
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import re

# Load environment variables
load_dotenv()

# OpenAI setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Database connection parameters
DB_PARAMS = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "dbname": os.getenv("POSTGRES_DB", "startup_intel"),
    "user": os.getenv("POSTGRES_USER", "startup"),
    "password": os.getenv("POSTGRES_PASSWORD", "secret"),
    "port": os.getenv("POSTGRES_PORT", 5432)
}

def extract_with_openai(tweet_text):
    prompt = f"""
Extract the following fields from this tweet:
- company_name
- round_amount
- currency
- round_type
- date (mentioned in text, else use today's date)
- investors (as a list)
- location (if mentioned)
- company_url (the official website domain of the company, e.g., "example.com"; if not found in the tweet, use web search to find the company's official website. If still unsure, return an empty string.)

Tweet: "{tweet_text}"

Return ONLY valid JSON, with no explanation or extra text.
"""
    response = client.responses.create(
        model="gpt-4.1",  # or "gpt-4o" if supported for web search
        tools=[{"type": "web_search_preview"}],
        input=prompt,
    )
    # The model's output is in response.output_text
    content = response.output_text.strip()
    print("OpenAI raw response:", content)  # Debug print

    # Remove code fences if present
    import re
    content = re.sub(r"^```(?:json)?\s*|```$", "", content.strip(), flags=re.MULTILINE).strip()

    return json.loads(content)

def process_tweets():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    cur.execute("""
        SELECT tweet_id, tweet_text, created_at
        FROM twitter_raw
        WHERE tweet_id NOT IN (
            SELECT tweet_id FROM twitter_processed
        );
    """)
    rows = cur.fetchall()

    for tweet_id, text, created_at in rows:
        enriched = extract_with_openai(text)

        final = {
            "tweet_id": tweet_id,
            "company_name": enriched.get("company_name"),
            "round_amount": enriched.get("round_amount"),
            "currency": enriched.get("currency"),
            "round_type": enriched.get("round_type"),
            "date": enriched.get("date") or created_at.date(),
            "investors": enriched.get("investors"),
            "location": enriched.get("location"),
            "source_url": f"https://twitter.com/i/web/status/{tweet_id}",
            "confidence": enriched.get("confidence"),
            "notes": enriched.get("notes"),
            "company_url": enriched.get("company_url")
        }

        cur.execute("""
            INSERT INTO twitter_processed (
                tweet_id, company_name, round_amount, currency,
                round_type, date, investors, location,
                source_url, confidence, notes, company_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [
            final["tweet_id"],
            final["company_name"],
            final["round_amount"],
            final["currency"],
            final["round_type"],
            final["date"],
            final["investors"],
            final["location"],
            final["source_url"],
            final["confidence"],
            final["notes"],
            final["company_url"]
        ])

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    process_tweets()
