"""
test_api_contract.py
--------------------
Validates that:
  1. POST /chat always returns the required fields.
  2. intent_detected values are always from the approved enum.
  3. suggested_actions always have label and number (with proper phone regex).
  4. source is always 'llm' or 'offline_template' or 'offline_json'.
  5. GET /health returns the expected shape.
  6. Multilingual inputs (Hindi, Assamese) return valid responses.
  7. LLM timeout / failure triggers offline fallback within time budget.

Uses FastAPI's TestClient — no real HTTP server needed.
Gemini is NOT called in these tests (no API key required).
"""

import re
import sys
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient

# Patch env before importing api so it starts without a real Gemini key
import os
os.environ.setdefault("GEMINI_API_KEY", "")  # empty = offline mode

from chatbot.api import app

client = TestClient(app)

# ─── Shared constants ────────────────────────────────────────────────────────

# NOTE: intent enum expanded to match backend capabilities (theft, robbery, assault added)
VALID_INTENTS = {
    "accident", "tyre_burst", "breakdown", "medical", "fire", "lost",
    "theft", "robbery", "assault", "suspicious_activity",
    "flood", "landslide", "other"
}
VALID_SOURCES = {"llm", "offline_template", "offline_json"}

REQUIRED_RESPONSE_FIELDS = {
    "session_id", "reply", "intent_detected", "suggested_actions", "source"
}

# Indian phone number regex: national short codes (3 digits) OR local numbers (7–15 digits)
# Accepts: "108", "100", "+91-9876543210", "03612-123456", "9876543210"
PHONE_REGEX = re.compile(r"^\+?[\d\s\-]{3,15}$")


# ─── Helper ──────────────────────────────────────────────────────────────────

def post_chat(message: str, context: dict | None = None, history: list | None = None):
    payload = {
        "session_id": "test-session-001",
        "user_message": message,
        "context": context or {},
        "history": history or [],
    }
    return client.post("/chat", json=payload)


# ─── Health check ────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_200(self):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_has_status_ok(self):
        r = client.get("/health")
        assert r.json()["status"] == "ok"

    def test_health_has_version(self):
        r = client.get("/health")
        assert "version" in r.json()


# ─── Response structure ──────────────────────────────────────────────────────

class TestResponseStructure:

    def test_all_required_fields_present(self):
        r = post_chat("I had an accident")
        assert r.status_code == 200
        data = r.json()
        for field in REQUIRED_RESPONSE_FIELDS:
            assert field in data, f"Missing field: {field}"

    def test_reply_is_non_empty_string(self):
        r = post_chat("My tyre burst")
        data = r.json()
        assert isinstance(data["reply"], str)
        assert len(data["reply"]) > 0

    def test_intent_detected_is_valid_enum(self):
        messages = [
            "accident on highway",
            "tyre puncture",
            "car broke down",
            "someone is bleeding",
            "vehicle on fire",
            "I am lost",
            "someone stole my bike",
            "robbery on the road",
            "hello",
        ]
        for msg in messages:
            r = post_chat(msg)
            intent = r.json()["intent_detected"]
            assert intent in VALID_INTENTS, f"Invalid intent '{intent}' for message: '{msg}'"

    def test_source_is_valid(self):
        r = post_chat("help me")
        assert r.json()["source"] in VALID_SOURCES

    def test_suggested_actions_is_list(self):
        r = post_chat("accident")
        assert isinstance(r.json()["suggested_actions"], list)

    def test_suggested_actions_have_label_and_number(self):
        r = post_chat("accident")
        for action in r.json()["suggested_actions"]:
            assert "label" in action, "Action missing 'label'"
            assert "number" in action, "Action missing 'number'"
            assert isinstance(action["label"], str)
            assert isinstance(action["number"], str)
            # Stronger phone validation: must match Indian number pattern
            number = action["number"].strip()
            assert PHONE_REGEX.match(number), (
                f"Phone number '{number}' does not match expected pattern. "
                "Must be 3–15 digits, optionally with +, spaces, or hyphens."
            )

    def test_session_id_echoed_back(self):
        r = post_chat("help")
        assert r.json()["session_id"] == "test-session-001"


# ─── Context handling ────────────────────────────────────────────────────────

class TestContextHandling:

    def test_request_with_full_context(self):
        ctx = {
            "lat": 26.321,
            "lng": 91.012,
            "state": "Assam",
            "district": "Barpeta",
            "nearest_highway": "NH-27",
            "is_sos_active": True,
        }
        r = post_chat("I had an accident", context=ctx)
        assert r.status_code == 200

    def test_request_with_empty_context(self):
        r = post_chat("breakdown", context={})
        assert r.status_code == 200

    def test_request_with_partial_context(self):
        r = post_chat("fire", context={"state": "Assam"})
        assert r.status_code == 200

    def test_context_lat_lng_none_safe(self):
        # lat=0.0 / lng=0.0 must not be treated as falsy (if lat and lng: bug)
        ctx = {"lat": 0.0, "lng": 0.0, "state": "Assam"}
        r = post_chat("accident near equator test", context=ctx)
        assert r.status_code == 200


# ─── Validation ──────────────────────────────────────────────────────────────

class TestValidation:

    def test_empty_message_rejected(self):
        r = client.post("/chat", json={
            "session_id": "x",
            "user_message": "",
            "context": {},
            "history": [],
        })
        assert r.status_code == 422  # Pydantic min_length=1

    def test_missing_user_message_rejected(self):
        r = client.post("/chat", json={"session_id": "x"})
        assert r.status_code == 422

    def test_history_with_messages(self):
        history = [
            {"role": "user", "content": "I crashed"},
            {"role": "assistant", "content": "Call 108 immediately."},
        ]
        r = post_chat("What should I do next?", history=history)
        assert r.status_code == 200

    def test_auto_generates_session_id_if_missing(self):
        r = client.post("/chat", json={"user_message": "help"})
        assert r.status_code == 200
        assert "session_id" in r.json()
        assert len(r.json()["session_id"]) > 0


# ─── Offline fallback (no API key) ──────────────────────────────────────────

class TestOfflineFallback:
    """When GEMINI_API_KEY is empty, all responses must come from offline templates."""

    def test_source_is_offline_when_no_key(self):
        r = post_chat("accident on the road")
        assert r.json()["source"] in ("offline_template", "offline_json")

    def test_reply_still_contains_emergency_number(self):
        r = post_chat("someone is unconscious and bleeding")
        reply = r.json()["reply"]
        # Should mention 108 in any medical offline template
        assert "108" in reply


# ─── Timeout / LLM failure fallback ─────────────────────────────────────────

class TestTimeoutFallback:
    """
    When the LLM call times out or raises an exception, the API must
    fall back to offline templates within the emergency response budget (5s).
    VERY important for emergency reliability — a stalled LLM cannot block help.
    """

    def test_llm_exception_triggers_offline_fallback(self):
        """Simulate LLM raising an exception — response must still succeed."""
        with patch("chatbot.api.call_llm", side_effect=Exception("Simulated LLM failure")):
            r = post_chat("accident on highway")
        assert r.status_code == 200
        data = r.json()
        assert data["source"] in ("offline_template", "offline_json")
        assert len(data["reply"]) > 0

    def test_llm_timeout_triggers_offline_fallback(self):
        """Simulate LLM timeout — response must arrive within 5 seconds."""
        import asyncio

        async def slow_llm(*args, **kwargs):
            await asyncio.sleep(10)  # longer than any acceptable timeout
            return "This should never be returned"

        with patch("chatbot.api.call_llm", side_effect=slow_llm):
            start = time.monotonic()
            r = post_chat("my car broke down")
            elapsed = time.monotonic() - start

        assert r.status_code == 200
        assert elapsed < 5.0, f"Response took {elapsed:.1f}s — too slow for an emergency app"
        assert r.json()["source"] in ("offline_template", "offline_json")

    def test_offline_fallback_contains_actionable_numbers(self):
        """Even in offline mode the reply must contain at least one emergency number."""
        with patch("chatbot.api.call_llm", side_effect=Exception("Simulated failure")):
            r = post_chat("fire in my vehicle")
        reply = r.json()["reply"]
        has_number = any(n in reply for n in ("100", "101", "108", "112", "1033"))
        assert has_number, "Offline fallback reply must include at least one emergency number"


# ─── Multilingual API tests ──────────────────────────────────────────────────

class TestMultilingualAPI:
    """
    The API must handle Hindi and Assamese inputs gracefully.
    Even in offline mode, a valid structured response is required.
    """

    def test_hindi_accident_returns_valid_response(self):
        r = post_chat("durghatna ho gayi sadak par")
        assert r.status_code == 200
        data = r.json()
        for field in REQUIRED_RESPONSE_FIELDS:
            assert field in data
        assert data["intent_detected"] in VALID_INTENTS

    def test_hindi_medical_returns_108(self):
        r = post_chat("chot lagi hai bahut khoon aa raha hai")
        assert r.status_code == 200
        data = r.json()
        assert data["intent_detected"] in ("medical", "accident", "other")
        # Medical reply in any language must surface 108
        assert "108" in data["reply"]

    def test_hindi_breakdown_returns_valid_response(self):
        r = post_chat("gaadi kharab ho gayi start nahi ho rahi")
        assert r.status_code == 200
        data = r.json()
        assert data["intent_detected"] in VALID_INTENTS
        assert data["source"] in VALID_SOURCES

    def test_assamese_accident_returns_valid_response(self):
        r = post_chat("durghotona hoise sadakot")
        assert r.status_code == 200
        data = r.json()
        for field in REQUIRED_RESPONSE_FIELDS:
            assert field in data
        assert data["intent_detected"] in VALID_INTENTS

    def test_assamese_fire_returns_valid_response(self):
        r = post_chat("garixot jui lagise")
        assert r.status_code == 200
        data = r.json()
        assert data["intent_detected"] in VALID_INTENTS
        assert len(data["reply"]) > 0

    def test_mixed_language_returns_valid_response(self):
        r = post_chat("meri gaadi mein accident ho gaya crash very bad")
        assert r.status_code == 200
        data = r.json()
        assert data["intent_detected"] in VALID_INTENTS


# ─── Police / theft intent API tests ────────────────────────────────────────

class TestPoliceTheftAPI:
    """
    Backend supports theft, robbery, assault — API contract must reflect this.
    """

    def test_theft_intent_returns_police_number(self):
        r = post_chat("someone stole my bike on the road")
        assert r.status_code == 200
        data = r.json()
        assert data["intent_detected"] in VALID_INTENTS
        # Theft response must surface police number
        numbers_in_reply = any(n in data["reply"] for n in ("100", "112"))
        numbers_in_actions = any(
            a["number"] in ("100", "112") for a in data["suggested_actions"]
        )
        assert numbers_in_reply or numbers_in_actions, (
            "Theft response must include police number (100 or 112)"
        )

    def test_robbery_returns_valid_response(self):
        r = post_chat("robbery happened, someone snatched my bag")
        assert r.status_code == 200
        data = r.json()
        assert data["intent_detected"] in VALID_INTENTS
        assert data["source"] in VALID_SOURCES

    def test_assault_returns_valid_response(self):
        r = post_chat("I was attacked and assaulted on the highway")
        assert r.status_code == 200
        data = r.json()
        assert data["intent_detected"] in VALID_INTENTS
        assert len(data["reply"]) > 0