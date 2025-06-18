import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def enrich_startup_description(name, website):
    prompt = f"Write a 1-sentence description of a startup named {name} with website {website}."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']
