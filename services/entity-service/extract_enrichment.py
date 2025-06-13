import os
import psycopg2
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

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

Return only valid JSON.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        return {"notes": f"OpenAI parsing error: {e}"}

def resolve_company_website(company_name):
    if not company_name:
        return None
    prompt = f"What is the official website URL of a company called '{company_name}'? Please return only domain when sure, example: 'example.com'. If not found or unsure, return nothing, like an empty string."
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error resolving domain for {company_name}: {e}")
        return None

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

        company_name = enriched.get("company_name")
        company_url = resolve_company_website(company_name)

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
            "company_url": company_url
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
