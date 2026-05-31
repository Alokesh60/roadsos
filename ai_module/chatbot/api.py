"""
api.py
------
RoadSOS AI Module — Secure FastAPI AI service.


Command:
py -m uvicorn chatbot.api:app --reload --port 8000

FIXES APPLIED (2026-05):
  #6  system_prompt was never reaching Gemini.
      `_call_gemini()` accepted system_prompt as a parameter but never
      used it. The global `gemini_client` was a bare GenerativeModel
      with no system_instruction, so every chat ran without any RoadSOS
      context (no GPS, no emergency numbers, no language lock, no rules).

      Root cause: `system_instruction` must be set on GenerativeModel at
      construction time — it cannot be injected via start_chat() or
      send_message(). The global client is therefore unsuitable for
      per-request system prompts.

      Fix: remove the bare global `gemini_client`. Keep a module-level
      flag `_gemini_ready` (bool) to track API key availability.
      In `_call_gemini()`, construct a fresh GenerativeModel with the
      request-specific system_instruction on every call. The overhead is
      negligible (no network round-trip at construction time).

  #7  `_call_gemini()` signature accepted `messages: list[dict]` but
      `start_chat(history=...)` expects the history *without* the final
      user turn, while `send_message()` sends the final user turn.
      The previous code sliced `messages[:-1]` for history and extracted
      `messages[-1]["parts"][0]["text"]` for the user turn — this is
      correct, but the approach only works when messages list has at
      least one entry. Added a guard to prevent IndexError on empty
      message lists.

  #8  Health endpoint now reflects true Gemini readiness via
      `_gemini_ready` flag instead of checking the (now-removed) global
      client object.
"""

from __future__ import annotations

import os
import asyncio
import logging
import uuid

from typing import Optional

import google.generativeai as genai

from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Depends
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from pydantic import (
    BaseModel,
    Field
)

from dotenv import load_dotenv

from chatbot.prompt_engine import (
    build_system_prompt,
    build_messages_payload
)

from chatbot.intent_classifier import (
    classify
)

from chatbot.response_templates import (
    get_template
)

from chatbot.retrieval import retrieve_top_k

# =====================================================
# LOAD ENV
# =====================================================

load_dotenv()

# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

log = logging.getLogger(__name__)

# =====================================================
# ENV VARIABLES
# =====================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
)

AI_MODULE_API_KEY = os.getenv(
    "AI_MODULE_API_KEY"
)

if not AI_MODULE_API_KEY:
    raise RuntimeError(
        "AI_MODULE_API_KEY environment variable is required."
    )

MAX_HISTORY_TURNS = int(
    os.getenv(
        "MAX_HISTORY_TURNS",
        "6"
    )
)

LLM_TIMEOUT = float(
    os.getenv(
        "LLM_TIMEOUT_SECONDS",
        "4"
    )
)

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "*"
).split(",")

# =====================================================
# GEMINI SETUP
# =====================================================

_gemini_ready = False

if GEMINI_API_KEY:

    genai.configure(
        api_key=GEMINI_API_KEY
    )

    _gemini_ready = True

    log.info(
        "Gemini API key configured. "
        "Models will be created per-request."
    )

else:

    log.warning(
        "GEMINI_API_KEY not found. "
        "Offline fallback enabled."
    )

# =====================================================
# REQUEST CONTEXT
# =====================================================

class Context(BaseModel):

    lat: Optional[float] = None

    lng: Optional[float] = None

    state: Optional[str] = None

    district: Optional[str] = None

    nearest_highway: Optional[str] = None

    nearest_hospital: Optional[str] = None

    nearest_hospital_phone: Optional[str] = None

    nearest_police_phone: Optional[str] = None

    nearest_ambulance_phone: Optional[str] = None

    nearest_towing_phone: Optional[str] = None

    is_sos_active: bool = False

    nearby_places: list[dict] = Field(
    default_factory=list
)


# =====================================================
# HISTORY MODEL
# =====================================================

class HistoryMessage(BaseModel):

    role: str

    content: str


# =====================================================
# CHAT REQUEST
# =====================================================

class ChatRequest(BaseModel):

    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())
    )

    user_message: str = Field(
        ...,
        min_length=1,
        max_length=1000
    )

    context: Context = Field(
        default_factory=Context
    )

    history: list[HistoryMessage] = Field(
        default_factory=list
    )


# =====================================================
# ACTION BUTTON
# =====================================================

class ActionButton(BaseModel):

    label: str

    number: str


# =====================================================
# CHAT RESPONSE
# =====================================================

class ChatResponse(BaseModel):

    session_id: str

    reply: str

    intent_detected: str

    detected_type: str

    priority: str

    suggested_actions: list[ActionButton]

    source: str


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title="RoadSOS AI Module",
    description="Emergency AI service",
    version="2.0.0"
)

# =====================================================
# SECURE CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# =====================================================
# AUTH VALIDATION
# =====================================================

def verify_backend_request(
    authorization: str = Header(None)
):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format"
        )

    token = authorization.replace("Bearer ", "")

    if token != AI_MODULE_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid AI module API key"
        )

    return True


# =====================================================
# ACTION BUTTONS
# =====================================================

def _build_suggested_actions(
    template_actions: list[dict]
):
    return [
        ActionButton(
            label=a["label"],
            number=a["number"]
        )
        for a in template_actions
    ]


# =====================================================
# PRIORITY MAPPING
# =====================================================

def determine_priority(intent: str):

    high_priority = {
        "accident",
        "medical",
        "fire",
        "crime"
    }

    medium_priority = {
        "vehicle_breakdown",
        "stranded"
    }

    if intent in high_priority:
        return "high"

    if intent in medium_priority:
        return "medium"

    return "low"


# =====================================================
# GEMINI CALL
# =====================================================
# FIX #6 (continued): system_prompt is now actually used.
# A new GenerativeModel is constructed per-request with
# system_instruction=system_prompt so that GPS context,
# emergency numbers, language lock, and all rules reach Gemini.
#
# FIX #7: Guard against empty messages list to prevent IndexError.

async def _call_gemini(
    system_prompt: str,
    messages: list[dict]
) -> str:

    if not _gemini_ready:
        raise RuntimeError("Gemini API key not configured.")

    if not messages:
        raise ValueError("messages list must not be empty.")

    def _sync_call() -> str:
        # Construct a per-request model with the full system prompt.
        # This is the ONLY way system_instruction reaches Gemini —
        # it cannot be set on start_chat() or send_message().
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_prompt,   # ← FIX #6 core change
        )

        # history = all turns except the final user message
        # last user message is sent via send_message()
        chat = model.start_chat(history=messages[:-1])

        last_user_text = messages[-1]["parts"][0]["text"]

        response = chat.send_message(
            last_user_text,
            generation_config={
                "max_output_tokens": 300,
                "temperature": 0.4,
            },
        )

        return response.text

    loop = asyncio.get_event_loop()

    reply = await asyncio.wait_for(
        loop.run_in_executor(None, _sync_call),
        timeout=LLM_TIMEOUT,
    )

    return reply


# =====================================================
# HEALTH CHECK
# =====================================================
# FIX #8: Use `_gemini_ready` flag instead of checking
# the (now-removed) global gemini_client object.

@app.api_route(
    "/health",
    methods=["GET", "HEAD"]
)
async def health():
    return {
        "status": "ok",
        "version": "2.0.0",
        "gemini_enabled": _gemini_ready,
    }


# =====================================================
# MAIN CHAT ENDPOINT
# =====================================================

@app.get("/test-gemini")
async def test_gemini():
    try:
        import google.generativeai as genai
        import os

        api_key = os.getenv("GEMINI_API_KEY")

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content("Say hello")

        return {
            "success": True,
            "reply": response.text
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest,
    authorized: bool = Depends(verify_backend_request)
):

    ctx = request.context

    log.info(
        f"Chat request received | session={request.session_id}"
    )

    # =================================================
    # INTENT CLASSIFICATION
    # =================================================

    intent, confidence = classify(request.user_message)

    log.info(f"Intent detected: {intent}")

    # =================================================
    # OFFLINE TEMPLATE
    # =================================================

    template = get_template(intent)

    suggested_actions = _build_suggested_actions([
        {
            "label": template["action_label"],
            "number": template["action_number"],
        },
        *template["extra_actions"],
    ])

    # =================================================
    # GEMINI PATH
    # =================================================

    if _gemini_ready:   # ← FIX #8: was `if GEMINI_API_KEY and gemini_client`

        try:
            retrieved_places = retrieve_top_k(
                request.user_message,
                ctx.nearby_places,
                k=3
            )
            log.info(
                f"Retrieved places count: {len(retrieved_places)}"
            )
            log.info(
                f"Retrieved places: {retrieved_places}"
            )

            system_prompt = build_system_prompt(
                lat=ctx.lat,
                lng=ctx.lng,
                state=ctx.state,
                district=ctx.district,
                nearest_highway=ctx.nearest_highway,
                nearest_hospital=ctx.nearest_hospital,
                nearest_hospital_phone=ctx.nearest_hospital_phone,
                nearest_police_phone=ctx.nearest_police_phone,
                nearest_ambulance_phone=ctx.nearest_ambulance_phone,
                nearest_towing_phone=ctx.nearest_towing_phone,
                is_sos_active=ctx.is_sos_active,
                nearby_places=retrieved_places
            )

            history_dicts = [
                {"role": m.role, "content": m.content}
                for m in request.history
            ]

            messages = build_messages_payload(
                system_prompt=system_prompt,
                history=history_dicts,
                user_message=request.user_message,
                max_turns=MAX_HISTORY_TURNS,
            )

            # system_prompt now flows into _call_gemini and is
            # applied as system_instruction on the GenerativeModel.
            reply = await _call_gemini(system_prompt, messages)

            log.info("Gemini reply generated.")

            return ChatResponse(
                session_id=request.session_id,
                reply=reply.strip(),
                intent_detected=intent,
                detected_type=intent,
                priority=determine_priority(intent),
                suggested_actions=suggested_actions,
                source="llm",
            )

        except asyncio.TimeoutError:
            log.warning("Gemini timeout — falling back to offline template.")

        except Exception as exc:
            log.error(f"Gemini error: {exc}")

    # =================================================
    # OFFLINE FALLBACK
    # =================================================

    log.info("Using offline fallback.")

    return ChatResponse(
        session_id=request.session_id,
        reply=template["reply"],
        intent_detected=intent,
        detected_type=intent,
        priority=determine_priority(intent),
        suggested_actions=suggested_actions,
        source="offline_template",
    )


# =====================================================
# DEV ENTRY
# =====================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "chatbot.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
