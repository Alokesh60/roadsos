"""
utils/classifier.py
--------------------
Detects whether an incoming message is a genuine emergency or a
fake/test/prank call — before the main chatbot response is generated.

Approach: Groq LLM call with a tightly constrained prompt.
Returns a structured dict, not a free-form string, so the Android app
and FastAPI can branch on it programmatically.

Why LLM and not a keyword list?
    Keyword lists miss context. "Testing 123" is fake. "I was testing my
    brakes and crashed" is real. The LLM handles this distinction; a
    keyword list does not.

Output shape:
    {
        "status":     "REAL" | "SUSPICIOUS" | "TEST",
        "confidence": 0.0–1.0,
        "reason":     "one sentence explanation",
        "proceed":    True | False    ← whether to run the full chatbot
    }

Policy:
    REAL        → proceed = True,  full chatbot response
    SUSPICIOUS  → proceed = True,  chatbot responds BUT adds a warning
    TEST        → proceed = False, return a canned "this is a test" reply

SUSPICIOUS is never silently dropped — someone genuinely scared may
phrase things oddly. When in doubt, help.
"""

from __future__ import annotations

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# utils/classifier.py — add below existing imports

SERIOUS_KEYWORDS = [
    "unconscious", "not breathing", "can't breathe", "bleeding heavily",
    "head injury", "cardiac", "heart attack", "seizure", "fracture",
    "broken bone", "crushed", "trapped", "critical", "severe",
    "chest pain", "spine", "neck injury", "multiple injuries", "not responding"
]

MINOR_KEYWORDS = [
    "scratch", "bruise", "minor", "small cut", "dent", "fender bender",
    "no injury", "just shaken", "superficial", "okay", "fine", "nothing serious"
]

def detect_severity(message: str) -> str:
    """
    Returns 'serious', 'minor', or 'default'.
    Keyword-first — no API call, zero latency.
    'default' when ambiguous or no signal found.
    """
    msg_lower = message.lower()

    serious_hits = sum(1 for kw in SERIOUS_KEYWORDS if kw in msg_lower)
    minor_hits = sum(1 for kw in MINOR_KEYWORDS if kw in msg_lower)

    if serious_hits > 0 and serious_hits >= minor_hits:
        return "serious"
    if minor_hits > 0 and serious_hits == 0:
        return "minor"
    return "default"

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------
_CLASSIFIER_SYSTEM = """
You are a fake emergency detector for a road accident SOS app.
Your job: classify whether the user message is a real emergency, a test, or suspicious.

Rules:
1. Classify as REAL if the message describes a genuine road accident, injury, or urgent need.
2. Classify as TEST if the message is clearly a test (e.g. "testing", "hello", "does this work", "1 2 3").
3. Classify as SUSPICIOUS if the message is ambiguous, joking, or seems like a prank but you cannot be sure.
4. When in doubt, prefer REAL over SUSPICIOUS. Never falsely classify a real emergency as TEST.
5. Respond ONLY with a JSON object — no explanation, no preamble, no markdown.

JSON format (exact):
{
  "status": "REAL" | "SUSPICIOUS" | "TEST",
  "confidence": <float 0.0 to 1.0>,
  "reason": "<one sentence>"
}
"""

_CANNED_TEST_RESPONSE = (
    "This appears to be a test message. RoadSoS is active and ready. "
    "In a real emergency, describe your situation and share your location. "
    "National emergency numbers: Ambulance 108, Police 100, Unified 112."
)

_SUSPICIOUS_WARNING = (
    "\n\n⚠️ Note: This message was flagged as potentially non-urgent. "
    "If this is a real emergency, call 112 immediately."
)


# ---------------------------------------------------------------------------
# Core classifier
# ---------------------------------------------------------------------------
def classify_emergency(message: str) -> dict:
    """
    Classify an incoming user message before the main chatbot runs.

    Parameters
    ----------
    message : raw user message from the Android app

    Returns
    -------
    dict with keys: status, confidence, reason, proceed
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": _CLASSIFIER_SYSTEM},
                {"role": "user",   "content": message}
            ],
            temperature=0.1,       # low temp — we want deterministic classification
            max_tokens=100         # JSON is tiny, no need for more
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if model adds them despite instructions
        raw = raw.replace("```json", "").replace("```", "").strip()

        result = json.loads(raw)

        # Validate expected keys
        status     = result.get("status", "REAL").upper()
        confidence = float(result.get("confidence", 0.5))
        reason     = result.get("reason", "")

        if status not in ("REAL", "SUSPICIOUS", "TEST"):
            status = "REAL"   # fail safe — unknown → treat as real

        return {
            "status":     status,
            "confidence": round(confidence, 2),
            "reason":     reason,
            "proceed":    status != "TEST",
        }

    except (json.JSONDecodeError, Exception):
        # If classifier fails for any reason, default to REAL — never block help
        return {
            "status":     "REAL",
            "confidence": 0.5,
            "reason":     "Classifier failed — defaulting to real emergency.",
            "proceed":    True,
        }


def get_canned_test_response() -> str:
    return _CANNED_TEST_RESPONSE


def get_suspicious_warning() -> str:
    return _SUSPICIOUS_WARNING



"""
INTEGRATION EXAMPLE (for chain.py or FastAPI endpoint):

from utils.classifier import classify_emergency, get_canned_test_response, get_suspicious_warning

classification = classify_emergency(user_message)

if not classification["proceed"]:
    # TEST detected — return canned response, don't call chatbot or scorer
    return get_canned_test_response()

# REAL or SUSPICIOUS — run full pipeline
reply = get_chat_response(
    message=user_message,
    lat=lat, lon=lon,
    nearby_facilities=ranked_facilities
)

if classification["status"] == "SUSPICIOUS":
    reply += get_suspicious_warning()

return reply
"""


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    TEST_MESSAGES = [
        "I've been in an accident, my car flipped, I'm bleeding",      # REAL
        "testing 123",                                                   # TEST
        "hello does this app work",                                      # TEST
        "my friend is unconscious after a crash on NH27",               # REAL
        "haha emergency lol just kidding",                               # SUSPICIOUS
        "I was testing my brakes and crashed into a divider, need help", # REAL — tricky
        "asdfjkl",                                                       # TEST
        "there's blood everywhere please help",                          # REAL
    ]

    print(f"\n{'Message':<55} {'Status':<12} {'Conf':<6} {'Reason'}")
    print("-" * 110)

    for msg in TEST_MESSAGES:
        result = classify_emergency(msg)
        short  = msg[:52] + "..." if len(msg) > 52 else msg
        print(
            f"{short:<55} {result['status']:<12} {result['confidence']:<6} {result['reason']}"
        )