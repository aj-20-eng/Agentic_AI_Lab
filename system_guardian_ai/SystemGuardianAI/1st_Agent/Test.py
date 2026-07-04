"""
test_connections.py — run this FIRST to verify both APIs work
before touching the full agent script.

Set your env vars first:
    export SERPAPI_KEY="..."
    export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
    export AZURE_OPENAI_API_KEY="..."
    export AZURE_OPENAI_DEPLOYMENT="LAB2"

Run:
    python test_connections.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()  # reads the .env file in the same folder and loads it into os.environ

def test_serpapi():
    print("Testing SerpApi...")
    params = {
        "engine": "google_flights",
        "departure_id": "DEL",
        "arrival_id": "BOM",
        "outbound_date": "2026-08-01",
        "type": "2",  # 2 = one-way (1 = round trip, which requires return_date)
        "currency": "INR",
        "hl": "en",
        "api_key": os.environ["SERPAPI_KEY"],
    }
    resp = requests.get("https://serpapi.com/search", params=params, timeout=30)
    if resp.status_code == 200 and ("best_flights" in resp.json() or "other_flights" in resp.json()):
        print("✅ SerpApi works — got flight data back.\n")
    else:
        print(f"❌ SerpApi issue. Status: {resp.status_code}")
        print(resp.text[:500], "\n")


def test_azure_openai():
    print("Testing Azure OpenAI...")
    from openai import AzureOpenAI
    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2024-08-01-preview",
    )
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "LAB2")
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": "Reply with just the word: OK"}],
        max_completion_tokens=5,
    )
    reply = response.choices[0].message.content
    print(f"✅ Azure OpenAI works — model replied: '{reply}'\n")


if __name__ == "__main__":
    try:
        test_serpapi()
    except Exception as e:
        print(f"❌ SerpApi failed: {e}\n")

    try:
        test_azure_openai()
    except Exception as e:
        print(f"❌ Azure OpenAI failed: {e}\n")