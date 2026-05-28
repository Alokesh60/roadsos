"""
api.py
------
RoadSOS AI Module — FastAPI server.

Run from:
D:\\roadsos\\ai_module

Command:
py -m uvicorn chatbot.api:app --reload --port 8000
"""

from __future__ import annotations

import os
import asyncio
import logging
import uuid

from typing import Optional

import google.generativeai as genai

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    classify,
    classify_from_json
)

from chatbot.response_templates import (
    get_template
)

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

# =====================================================
# GEMINI SETUP
# =====================================================

if GEMINI_API_KEY:

    genai.configure(
        api_key=GEMINI_API_KEY
    )

    gemini_client = genai.GenerativeModel(
        "models/gemini-2.0-flash"
    )

    log.info(
        "Gemini initialized successfully."
    )

else:

    gemini_client = None

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

    is_sos_active: bool = False


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

    suggested_actions: list[ActionButton]

    source: str


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(

    title="RoadSOS AI Module",

    description="Emergency chatbot API",

    version="1.0.0"
)

# =====================================================
# CORS
# =====================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_methods=["*"],

    allow_headers=["*"],
)

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
# GEMINI CALL
# =====================================================

async def _call_gemini(

    system_prompt: str,

    messages: list[dict]
):

    if gemini_client is None:

        raise RuntimeError(
            "Gemini client not initialized"
        )

    def _sync_call():

        chat = gemini_client.start_chat(

            history=messages[:-1]
        )

        last_user_text = (

            messages[-1]["parts"][0]["text"]
        )

        response = chat.send_message(

            last_user_text,

            generation_config={

                "max_output_tokens": 300,

                "temperature": 0.4
            }
        )

        return response.text

    loop = asyncio.get_event_loop()

    reply = await asyncio.wait_for(

        loop.run_in_executor(
            None,
            _sync_call
        ),

        timeout=LLM_TIMEOUT
    )

    return reply


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")

async def health():

    return {

        "status": "ok",

        "version": "1.0.0",

        "gemini_enabled":
            gemini_client is not None
    }


# =====================================================
# MAIN CHAT ENDPOINT
# =====================================================

@app.post(

    "/chat",

    response_model=ChatResponse
)

async def chat(request: ChatRequest):

    ctx = request.context

    log.info(

        f"Chat request: "
        f"{request.user_message}"
    )

    # =================================================
    # INTENT CLASSIFICATION
    # =================================================

    intent, confidence = classify(

        request.user_message
    )

    log.info(

        f"Intent detected: "
        f"{intent}"
    )

    # =================================================
    # OFFLINE TEMPLATE
    # =================================================

    template = get_template(intent)

    suggested_actions = (
        _build_suggested_actions([
            {

                "label":
                    template["action_label"],

                "number":
                    template["action_number"]
            },

            *template["extra_actions"]
        ])
    )

    # =================================================
    # GEMINI PATH
    # =================================================

    if GEMINI_API_KEY and gemini_client:

        try:

            system_prompt = (

                build_system_prompt(

                    lat=ctx.lat,

                    lng=ctx.lng,

                    state=ctx.state,

                    district=ctx.district,

                    nearest_highway=(
                        ctx.nearest_highway
                    ),

                    nearest_hospital=(
                        ctx.nearest_hospital
                    ),

                    nearest_hospital_phone=(
                        ctx.nearest_hospital_phone
                    ),

                    nearest_police_phone=(
                        ctx.nearest_police_phone
                    ),

                    is_sos_active=(
                        ctx.is_sos_active
                    )
                )
            )

            history_dicts = [

                {

                    "role":
                        m.role,

                    "content":
                        m.content
                }

                for m in request.history
            ]

            messages = (

                build_messages_payload(

                    system_prompt=system_prompt,

                    history=history_dicts,

                    user_message=(
                        request.user_message
                    ),

                    max_turns=(
                        MAX_HISTORY_TURNS
                    )
                )
            )

            reply = await _call_gemini(

                system_prompt,

                messages
            )

            log.info(
                "Gemini reply generated."
            )

            return ChatResponse(

                session_id=request.session_id,

                reply=reply.strip(),

                intent_detected=intent,

                suggested_actions=(
                    suggested_actions
                ),

                source="llm"
            )

        except asyncio.TimeoutError:

            log.warning(
                "Gemini timeout."
            )

        except Exception as exc:

            log.error(
                f"Gemini error: {exc}"
            )

    # =================================================
    # OFFLINE FALLBACK
    # =================================================

    log.info(
        "Using offline fallback."
    )

    return ChatResponse(

        session_id=request.session_id,

        reply=template["reply"],

        intent_detected=intent,

        suggested_actions=(
            suggested_actions
        ),

        source="offline_template"
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

        reload=True
    )