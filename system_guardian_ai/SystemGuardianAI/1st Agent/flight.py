"""
flight_finder_agent.py

A minimal ReAct-style agentic AI that finds the cheapest flight
across sources and hands you a real, working booking link.

WHY THIS COUNTS AS "AGENTIC":
- The LLM decides WHEN to call each tool (not us hardcoding the calls)
- The LLM decides WHAT to do with the results (resolve city->code, sort, compare, pick)
- The LLM chains TWO tool calls in sequence: search_flights -> get_booking_link
- The LLM decides WHEN it's done and produces a final answer
- We just run the loop: think -> act -> observe -> repeat

Data source: SerpApi's Google Flights engine. Google Flights already
aggregates prices from airlines + OTAs (MakeMyTrip, Cleartrip, etc.),
so one API call effectively covers "many websites" without needing
fragile per-site scraping.

SETUP:
    pip install requests openai python-dotenv

    Get a free SerpApi key (100 searches/month free):
    https://serpapi.com/users/sign_up

    Put these in a .env file in the same folder:
    SERPAPI_KEY=your_serpapi_key
    AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
    AZURE_OPENAI_API_KEY=your_azure_key
    AZURE_OPENAI_DEPLOYMENT=gpt-5.4-mini

RUN:
    python flight_finder_agent.py
"""

import os
import json
import requests
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()  # reads the .env file in the same folder and loads it into os.environ

# ---------------------------------------------------------------------------
# 1. THE TOOLS — these are the agent's "hands" reaching out into the world.
#    Each is a normal Python function, plus a schema describing it so the
#    LLM can decide when and how to call it.
# ---------------------------------------------------------------------------

def search_flights(origin: str, destination: str, date: str) -> str:
    """Search flights via SerpApi's Google Flights engine and return raw results as JSON string."""
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": date,
        "type": "2",  # 2 = one-way (1 = round trip, which requires return_date)
        "currency": "INR",
        "hl": "en",
        "api_key": os.environ["SERPAPI_KEY"],
    }
    resp = requests.get("https://serpapi.com/search", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    flights = data.get("best_flights", []) + data.get("other_flights", [])

    # Trim to only what the agent needs to reason over (keeps context small)
    simplified = []
    for f in flights:
        legs = f.get("flights", [])
        if not legs:
            continue
        simplified.append({
            "airline": legs[0].get("airline"),
            "price_inr": f.get("price"),
            "duration_minutes": f.get("total_duration"),
            "departure_time": legs[0].get("departure_airport", {}).get("time"),
            "arrival_time": legs[-1].get("arrival_airport", {}).get("time"),
            "booking_token": f.get("booking_token"),  # needed to fetch a real booking link
        })

    return json.dumps(simplified)


def build_flight_search_url(origin: str, destination: str, date: str) -> str:
    """
    Build a stable Google Flights search URL (pre-filled with route + date).
    Unlike booking_token-based links, this never expires and always works,
    since it's just Google Flights' normal search page with query params —
    not a session-bound click-tracking redirect.
    """
    query = f"One way flights from {origin} to {destination} on {date}"
    url = "https://www.google.com/travel/flights?q=" + requests.utils.quote(query)
    return json.dumps({"search_url": url})


# Schemas the LLM uses to know each tool exists and how to call it
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_flights",
            "description": "Search for flights between two airports on a given date. Returns a list of flight options with price, airline, timing, and a booking_token for each.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Origin airport IATA code, e.g. DEL"},
                    "destination": {"type": "string", "description": "Destination airport IATA code, e.g. BOM"},
                    "date": {"type": "string", "description": "Departure date in YYYY-MM-DD format"},
                },
                "required": ["origin", "destination", "date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_flight_search_url",
            "description": "Builds a stable Google Flights search URL for a given route and date. Use this to give the user a working link, instead of trying to construct a link from a booking_token (those expire and don't work when opened directly).",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Origin airport IATA code, e.g. DEL"},
                    "destination": {"type": "string", "description": "Destination airport IATA code, e.g. BOM"},
                    "date": {"type": "string", "description": "Departure date in YYYY-MM-DD format"},
                },
                "required": ["origin", "destination", "date"],
            },
        },
    },
]

AVAILABLE_FUNCTIONS = {
    "search_flights": search_flights,
    "build_flight_search_url": build_flight_search_url,
}


# ---------------------------------------------------------------------------
# 2. THE AGENT LOOP (ReAct: Reason -> Act -> Observe -> repeat)
# ---------------------------------------------------------------------------

def run_agent(user_request: str) -> str:
    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2024-08-01-preview",
    )
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4-mini")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a flight-booking assistant. The user will give you city names "
                "(not airport codes) for origin and destination, plus a date. "
                "STEP 1: convert each city name to its primary IATA airport code using your "
                "own knowledge (e.g. Patna -> PAT, Mumbai -> BOM, Delhi -> DEL, Bangalore -> BLR, Goa -> GOI). "
                "If a city has multiple airports, pick the main/most common one. "
                "STEP 2: call search_flights with those IATA codes and the date. "
                "STEP 3: from the results, pick the CHEAPEST option. "
                "STEP 4: call build_flight_search_url with the same origin/destination/date "
                "to get a stable, working Google Flights search link. "
                "STEP 5: reply with the city names, airline, price, departure/arrival time, and the "
                "search URL from build_flight_search_url, noting the user can select this exact flight "
                "on that page. "
                "Assume dates without a year are in the near future. "
                "If something is missing or unclear, say so honestly. Keep the final answer short."
            ),
        },
        {"role": "user", "content": user_request},
    ]

    max_turns = 6
    for turn in range(max_turns):
        response = client.chat.completions.create(
            model=deployment,
            messages=messages,
            tools=TOOLS,
        )
        msg = response.choices[0].message
        messages.append(msg)

        # --- REASON: did the model decide to ACT (call a tool)? ---
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                print(f"[agent] Turn {turn+1}: calling {fn_name}({fn_args})")

                # --- ACT ---
                result = AVAILABLE_FUNCTIONS[fn_name](**fn_args)

                # --- OBSERVE: feed the tool's result back to the model ---
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
            continue  # loop back so the model can reason over the observation

        # --- No tool call means the model thinks it's done ---
        return msg.content

    return "Agent stopped after max turns without a final answer."


def find_cheapest_flight(origin_city: str, destination_city: str, date: str) -> str:
    """
    Programmatic entry point — pass city names directly (e.g. "Patna", "Mumbai").
    The agent resolves city names to IATA codes, searches, picks cheapest,
    then resolves a real booking link — all as its own reasoning/tool-call chain.
    """
    user_request = (
        f"Find the cheapest flight from {origin_city} to {destination_city} on {date}."
    )
    return run_agent(user_request)


if __name__ == "__main__":
    origin_city = input("Origin city (e.g. Patna): ").strip()
    destination_city = input("Destination city (e.g. Mumbai): ").strip()
    date = input("Date (YYYY-MM-DD): ").strip()

    answer = find_cheapest_flight(origin_city, destination_city, date)
    print("\n--- FINAL ANSWER ---")
    print(answer)