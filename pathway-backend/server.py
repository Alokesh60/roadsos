from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import json
import os

load_dotenv()

app = FastAPI()

DATA_DIR = Path("data/places")
DATA_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    model = None


class Place(BaseModel):
    id: str
    name: str
    category: str
    phone: Optional[str] = ""
    address: Optional[str] = ""
    latitude: float
    longitude: float
    distance_km: float


class UpdatePlacesRequest(BaseModel):
    user_id: str
    latitude: float
    longitude: float
    timestamp: Optional[str] = None
    places: List[Place]


class ChatRequest(BaseModel):
    user_id: str
    message: str


@app.get("/")
def root():
    return {"status": "running"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "gemini_enabled": model is not None
    }


@app.post("/update_places")
def update_places(request: UpdatePlacesRequest):

    file_path = DATA_DIR / f"{request.user_id}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(request.model_dump(), f, indent=2)

    return {
        "success": True,
        "places_received": len(request.places)
    }


@app.post("/chat")
@app.post("/chat")
def chat(request: ChatRequest):

    file_path = DATA_DIR / f"{request.user_id}.json"

    if not file_path.exists():
        return {
            "response": "No nearby services available."
        }

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    services = data["places"]

    # Sort nearest first
    services = sorted(
        services,
        key=lambda x: x["distance_km"]
    )

    msg = request.message.lower()

    target_category = None

    # Medical intent
    if any(word in msg for word in [
        "hospital", "doctor", "medical",
        "injury", "injured", "ambulance",
        "accident", "bleeding"
    ]):
        target_category = "Hospital"

    # Police intent
    elif any(word in msg for word in [
        "police", "crime", "theft",
        "robbery", "attack", "stolen"
    ]):
        target_category = "Police"

    # Vehicle breakdown intent
    elif any(word in msg for word in [
        "garage", "repair", "mechanic",
        "breakdown", "broke down",
        "car problem", "vehicle problem",
        "engine", "tire", "puncture"
    ]):
        target_category = "Garage"

    # Food intent
    elif any(word in msg for word in [
        "food", "restaurant",
        "eat", "hungry"
    ]):
        target_category = "Food"

    # --------------------------
    # CATEGORY RETRIEVAL
    # --------------------------

    if target_category:

        filtered = [
            s for s in services
            if s["category"].lower() == target_category.lower()
        ]

        # Do NOT call Gemini if nothing found
        if len(filtered) == 0:

            available_categories = sorted(
                list(
                    set(
                        s["category"]
                        for s in services
                    )
                )
            )

            return {
                "response":
                    f"No nearby {target_category.lower()} services are available. "
                    f"Available categories: {', '.join(available_categories)}."
            }

        top_k = filtered[:3]

    else:

        # Generic emergency query
        top_k = services[:5]

    # --------------------------
    # BUILD CONTEXT
    # --------------------------

    context = "Nearby Services:\n\n"

    for idx, service in enumerate(top_k, start=1):

        context += (
            f"{idx}. {service['name']}\n"
            f"Category: {service['category']}\n"
            f"Distance: {service['distance_km']} km\n"
            f"Phone: {service.get('phone', '')}\n"
            f"Address: {service.get('address', '')}\n\n"
        )

    prompt = f"""
You are RoadSOS.

{context}

User Question:
{request.message}

Rules:
1. Use ONLY the services listed above.
2. Never invent locations, phone numbers, hospitals, police stations or garages.
3. If information is unavailable, clearly say so.
4. Prefer nearest services first.
5. Keep response under 80 words.
6. Do not ask follow-up questions.
"""

    if model is None:
        return {
            "response": "Gemini API key not configured."
        }

    try:

        response = model.generate_content(prompt)

        return {
            "response": response.text
        }

    except Exception as e:

        return {
            "response": f"Gemini error: {str(e)}"
        }