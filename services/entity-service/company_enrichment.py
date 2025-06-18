import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def fetch_website_text(url: str, max_chars: int = 3000) -> str:
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "header", "footer", "nav"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        return " ".join(text.split())[:max_chars]
    except Exception as e:
        return f"Error fetching content: {e}"

def extract_company_info(text: str):
    prompt = f"""
You are a company profiling assistant. Given this homepage content, extract:
- A 1-2 sentence company description
- The company's HQ location (city, state/country)
- 2-4 industry tags

Text:
{text}

Return as JSON with keys: description, location, tags
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        return eval(response.choices[0].message.content)
    except Exception as e:
        return {"error": f"OpenAI parsing failed: {e}"}

if __name__ == "__main__":
    homepage = "https://example.com"
    raw_text = fetch_website_text(homepage)
    enriched = extract_company_info(raw_text)
    print(enriched)
