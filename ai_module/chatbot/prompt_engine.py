"""
prompt_engine.py
----------------
Builds the system prompt sent to the Gemini LLM.
Injects GPS context, nearest facilities, state/district,
and highway information so the AI gives location-specific advice.

The system prompt is intentionally concise to reduce token count
and keep LLM latency low (target: under 4 seconds round-trip).

FIXES APPLIED (2026-05):
  #1  GPS zero-coordinate bug: `if lat and lng` evaluates to False
      when lat/lng is 0.0 (equator/prime meridian). Fixed to
      `if lat is not None and lng is not None`.

  #2  Language instruction was too weak ("Respond in the SAME LANGUAGE").
      LLMs drift on Assamese/Hindi. Replaced with an explicit lock:
      detect once, never switch unless user explicitly changes language.

  #3  Role section was too generic ("road emergencies" only).
      Backend already supports theft, robbery, assault, SOS escalation.
      Prompt now matches backend capabilities.

  #4  "Do NOT say 'I don't know'" creates hallucination pressure.
      Replaced with: state the limitation, give safest general guidance.

  #5  build_messages_payload() note added: system_prompt must be passed
      as the first user-turn injection when using the new Gemini SDK,
      since it does not have a native system role in messages[]. Test
      carefully against your SDK version.
"""

from __future__ import annotations
from typing import Optional


# ─── Shared emergency numbers always included in context ───────────────────
NATIONAL_NUMBERS = {
    "ambulance": "108",
    "police": "100",
    "fire": "101",
    "highway": "1033 (NHAI)",
    "unified": "112",
}


def build_system_prompt(
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    nearest_highway: Optional[str] = None,
    nearest_hospital: Optional[str] = None,
    nearest_hospital_phone: Optional[str] = None,
    nearest_police_phone: Optional[str] = None,
    nearest_ambulance_phone: Optional[str] = None,
    nearest_towing_phone: Optional[str] = None,
    is_sos_active: bool = False,
    nearby_places: Optional[list] = None,
) -> str:
    """
    Build a system prompt for the Gemini LLM.

    Args:
        lat, lng               : User's GPS coordinates (float, can be None).
                                 NOTE: use `is not None` checks — 0.0 is a
                                 valid coordinate but evaluates falsy.
        state                  : State name e.g. "Assam"
        district               : District name e.g. "Barpeta"
        nearest_highway        : e.g. "NH-27"
        nearest_hospital       : Name of nearest hospital from Places API
        nearest_hospital_phone : Phone number of nearest hospital
        nearest_police_phone   : Phone number of nearest police station
        nearest_ambulance_phone: Phone number of nearest ambulance service
        nearest_towing_phone   : Phone number of nearest towing service
        is_sos_active          : Whether the user has already triggered SOS

    Returns:
        System prompt string
    """

    # ── FIX #1: use `is not None` — lat/lng == 0.0 is valid but falsy ──
    location_parts = []
    if district:
        location_parts.append(district)
    if state:
        location_parts.append(state)
    if lat is not None and lng is not None:          # ← was: `if lat and lng`
        location_parts.append(f"GPS: {lat:.4f}, {lng:.4f}")
    location_str = ", ".join(location_parts) if location_parts else "India (location unknown)"

    highway_str = f" on or near {nearest_highway}" if nearest_highway else ""

    # Build nearest facility strings
    hosp_str = ""
    if nearest_hospital:
        hosp_str = f"\n- Nearest hospital: {nearest_hospital}"
        if nearest_hospital_phone:
            hosp_str += f" ({nearest_hospital_phone})"

    police_str = ""
    if nearest_police_phone:
        police_str = f"\n- Nearest police: {nearest_police_phone}"

    ambulance_str = ""
    if nearest_ambulance_phone:
        ambulance_str = f"\n- Nearest ambulance: {nearest_ambulance_phone}"

    towing_str = ""
    if nearest_towing_phone:
        towing_str = f"\n- Nearest towing: {nearest_towing_phone}"

    sos_note = ""
    if is_sos_active:
        sos_note = (
            "\n\nNOTE: The user has already triggered an SOS alert. "
            "Emergency contacts have been notified. "
            "Focus on keeping the user calm and giving first-response guidance "
            "while help is on the way."
        )

        # ── NEARBY SERVICES CONTEXT ───────────────────────────

    services_context = ""

    if nearby_places:

        services_context = "\n\nNEARBY SERVICES:\n"

        for idx, place in enumerate(
            nearby_places[:5],
            start=1
        ):

            services_context += (
                f"\n{idx}. {place.get('name', 'Unknown')}"
                f"\nCategory: {place.get('category', 'Unknown')}"
                f"\nDistance: {place.get('distanceMeters', '?')} meters"
                f"\nETA: {place.get('estimatedEtaMinutes', 'N/A')} minutes"
                f"\nRating: {place.get('rating', 'N/A')}"
                f"\nOpen Now: {place.get('isOpenNow', 'Unknown')}"
                f"\nPhone: {place.get('phone', 'N/A')}\n"
            )

    # ── FIX #2: explicit language lock ─────────────────────────────────────
    # Old: "Respond in the SAME LANGUAGE the user writes in"
    # Problem: LLMs drift — especially on Assamese and mixed Hindi/English.
    language_rule = (
        "LANGUAGE RULE:\n"
        "Detect the user's language from their FIRST message and lock to it "
        "for the entire conversation. Never switch languages unless the user "
        "explicitly writes in a different language. "
        "Supported languages: English, Hindi (Devanagari or Roman), Assamese. "
        "If the language is unclear, default to English."
    )

    # ── FIX #3: expanded role section ──────────────────────────────────────
    # Old: only "road emergencies: accidents, medical crises, vehicle fires,
    #           breakdowns, tyre bursts"
    # Added: theft/robbery/assault, SOS escalation, roadside assistance
    role_section = (
        "YOUR ROLE:\n"
        "- Respond to road emergencies: accidents, medical crises, vehicle fires, "
        "breakdowns, tyre bursts.\n"
        "- Handle police emergencies such as theft, robbery, assault, and "
        "suspicious activity on or near roads.\n"
        "- Handle roadside assistance situations including breakdowns, punctures, "
        "and towing requests.\n"
        "- If SOS is already active, prioritise calm reassurance and immediate "
        "survival guidance while help is on the way.\n"
        "- Give clear, numbered, actionable steps. Be calm and direct.\n"
        "- Always recommend calling 108 for medical emergencies, 100 for police.\n"
        "- Use local/nearest numbers when available (listed above).\n"
        "- Keep replies concise — the user may be in a panic. Max 150 words.\n"
        "- At the end of every reply, include the single most important action "
        "they should take right now."
    )

    # ── FIX #4: hallucination guard ────────────────────────────────────────
    # Old: "Do NOT say 'I don't know' — always give the best advice you can"
    # Problem: forces the model to generate something even when it has nothing
    # reliable, creating hallucination pressure (e.g. inventing phone numbers).
    hallucination_rule = (
        "- If exact information is unavailable, clearly state the limitation "
        "and provide the safest general emergency guidance possible "
        "(e.g. 'I don't have the local number, but call 112 now')."
    )

    prompt = f"""You are RoadSOS, an emergency response AI assistant for Indian roads.

CURRENT USER LOCATION: {location_str}{highway_str}

AVAILABLE EMERGENCY CONTACTS:
- Ambulance (national): 108
- Police (national): 100
- Fire (national): 101
- NHAI Highway Helpline: 1033
- Unified Emergency: 112{hosp_str}{police_str}{ambulance_str}{towing_str}{sos_note}

{services_context}

{role_section}

STRICT RULES:
- Do NOT give medical diagnoses.
- Do NOT make up phone numbers — only use the numbers listed above.
- Use ONLY the nearby services listed in the NEARBY SERVICES section.
- Never invent hospitals, police stations, garages, food points, addresses or contact numbers.
- If a requested category is unavailable, clearly state that no nearby service of that type is available.
- When the user asks for the nearest or closest service, prioritize distance.
- When the user asks for the best, top, recommended, or highest rated service, prioritize rating.
- When mentioning a service, include its distance if available.
{hallucination_rule}
- If the situation is life-threatening, lead with "Call 108 NOW." on the first line.
{language_rule}
"""

    return prompt.strip()


def build_messages_payload(
    system_prompt: str,
    history: list[dict],
    user_message: str,
    max_turns: int = 6,
) -> list[dict]:
    """
    Build the messages list for the Gemini API.
    Trims history to the last `max_turns` turns (user+assistant pairs).

    Args:
        system_prompt : The system prompt string
        history       : List of {"role": "user"|"assistant", "content": "..."}
        user_message  : The current user message
        max_turns     : Max history pairs to include

    Returns:
        List of message dicts ready for Gemini SDK

    FIX #5 — SYSTEM PROMPT INJECTION NOTE:
        The current implementation does NOT inject system_prompt into the
        messages list. This works with the new Gemini SDK (which accepts
        system_instruction as a separate parameter), but may fail subtly
        with older SDK versions or if the caller forgets to pass
        system_instruction separately.

        Recommended pattern when calling the Gemini SDK:

            response = model.generate_content(
                contents=messages,
                generation_config=...,
                system_instruction=system_prompt,   # <-- pass here
            )

        Do NOT prepend system_prompt as a user message — it degrades
        response quality and bloats history trimming. Test your SDK
        version explicitly.
    """
    # Trim history: keep last max_turns * 2 messages (user + assistant pairs)
    trimmed = history[-(max_turns * 2):]

    messages = []

    # Gemini uses "user" and "model" roles
    role_map = {"user": "user", "assistant": "model"}

    for msg in trimmed:
        role = role_map.get(msg.get("role", "user"), "user")
        content = msg.get("content", "")
        if content:
            messages.append({"role": role, "parts": [{"text": content}]})

    # Append the current user message
    messages.append({"role": "user", "parts": [{"text": user_message}]})

    return messages