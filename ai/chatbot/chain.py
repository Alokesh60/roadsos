"""
chatbot/chain.py
----------------
Groq-backed emergency assistant.

Key change from Day 4:
    get_chat_response() now accepts nearby_facilities — the output of
    scorer.to_api_response(). The LLM formats and advises; it never
    invents distances, names, or phone numbers.

If nearby_facilities is None or empty, the response will explicitly tell
the user that no verified facilities were found nearby, rather than
hallucinating data. This is intentional.

Day 5 update:
    severity parameter now injected into user_content so LLM tone and
    priority guidance matches the actual emergency level.
"""

import os
import json
import yaml
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

with open(os.path.join(os.path.dirname(__file__), "prompts/system_prompt.yaml"), "r") as f:
    prompt_config = yaml.safe_load(f)
    SYSTEM_PROMPT = prompt_config["system_prompt"]


def _format_facilities(facilities: list[dict]) -> str:
    """
    Converts scorer output into a clean, LLM-readable block.
    Limits to top 5 to stay within token budget.
    """
    top = facilities[:5]
    lines = []
    for i, fac in enumerate(top, 1):
        name      = fac.get("name", "Unknown")
        ftype     = fac.get("facility_type", "facility")
        dist      = fac.get("distance_km", "?")
        phone     = fac.get("phone", "N/A")
        address   = fac.get("address", "N/A")
        available = fac.get("is_available")
        rating    = fac.get("rating", "N/A")
        resp_t    = fac.get("response_time_min", "unknown")

        avail_str = "Open" if available else ("Closed" if available is False else "Unknown")

        lines.append(
            f"{i}. {name} ({ftype})\n"
            f"   Distance: {dist} km | Rating: {rating}/5 | Status: {avail_str}\n"
            f"   Response time: {resp_t} min | Phone: {phone}\n"
            f"   Address: {address}"
        )
    return "\n\n".join(lines)


def get_chat_response(
    message: str,
    lat: float,
    lon: float,
    nearby_facilities: list[dict] | None = None,
    severity: str = "default",
) -> str:
    """
    Parameters
    ----------
    message           : user's emergency message
    lat, lon          : user's GPS coordinates
    nearby_facilities : output of scorer.to_api_response() — pre-ranked DB results.
                        Pass None only during development/testing.
    severity          : 'serious', 'minor', or 'default' — from detect_severity()
                        Injected into prompt so LLM tone matches emergency level.

    Returns
    -------
    LLM response string.
    """

    severity_context = {
        "serious": "SEVERITY: SERIOUS — life-threatening emergency. Use urgent tone. Facilities are already ranked correctly for this severity. Do not reorder them.",
        "minor":   "SEVERITY: MINOR — no immediate life threat. Closest facility is priority.",
        "default": "SEVERITY: UNKNOWN — treat as potentially serious until confirmed otherwise.",
    }.get(severity, "SEVERITY: UNKNOWN — treat as potentially serious until confirmed otherwise.")

    if nearby_facilities:
        facility_block = _format_facilities(nearby_facilities)
        user_content = (
            f"{severity_context}\n\n"
            f"User location: lat={lat}, lon={lon}\n\n"
            f"VERIFIED NEARBY FACILITIES (ranked by proximity, rating, and availability):\n"
            f"{facility_block}\n\n"
            f"User message: {message}"
        )
    else:
        # No DB data — tell LLM explicitly so it doesn't hallucinate
        user_content = (
            f"{severity_context}\n\n"
            f"User location: lat={lat}, lon={lon}\n\n"
            f"VERIFIED NEARBY FACILITIES: None found in database for this location.\n\n"
            f"User message: {message}"
        )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        temperature=0.3,
        max_tokens=512
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Smoke test — uses scorer mock data directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Simulate what Alokesh's backend will pass after scorer runs
    MOCK_SCORED = [
        {
            "name": "GMCH Guwahati",
            "facility_type": "hospital",
            "distance_km": 1.43,
            "rating": 4.2,
            "response_time_min": 8,
            "is_available": True,
            "phone": "0361-2529457",
            "address": "Bhangagarh, Guwahati",
            "score": 0.8801
        },
        {
            "name": "Downtown Hospital",
            "facility_type": "hospital",
            "distance_km": 5.03,
            "rating": 4.5,
            "response_time_min": None,
            "is_available": True,
            "phone": "0361-2331003",
            "address": "Dispur, Guwahati",
            "score": 0.7171
        },
    ]

    # Test serious severity
    print("\n--- Serious Severity Test ---")
    reply = get_chat_response(
        message="Person is unconscious and bleeding heavily",
        lat=26.1480,
        lon=91.7500,
        nearby_facilities=MOCK_SCORED,
        severity="serious"
    )
    print(reply)

    # Test minor severity
    print("\n--- Minor Severity Test ---")
    reply = get_chat_response(
        message="Minor fender bender, no injuries just need towing",
        lat=26.1480,
        lon=91.7500,
        nearby_facilities=MOCK_SCORED,
        severity="minor"
    )
    print(reply)