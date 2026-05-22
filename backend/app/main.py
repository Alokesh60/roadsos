from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.nearby import router as nearby_router
from app.api.search import router as search_router
from app.api.download import router as download_router
from app.api.auth import router as auth_router
from app.middleware.cors import setup_cors
from app.api.emergency import router as emergency_router
from app.api.semantic import router as semantic_router
from app.api.ai_emergency import router as ai_emergency_router
from app.api.chatbot import router as chatbot_router
from app.services.sqlite_service import get_all_services
from ai.embeddings.chroma_setup import build_index
from app.api.sos import router as sos_router
from app.api.contacts import router as contacts_router

# Initialize the ChromaDB index
services = get_all_services()
build_index(services)

app = FastAPI(
    title="RoadSoS API",
    description="Emergency Road Safety Backend",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():

    print("\n[Startup] Loading emergency services...")

    services = get_all_services()

    print(
        f"[Startup] Found {len(services)} services."
    )

    print("[Startup] Building ChromaDB index...")

    build_index(services)

    print("[Startup] ChromaDB ready.\n")

setup_cors(app)

app.include_router(health_router)
app.include_router(nearby_router)
app.include_router(search_router)
app.include_router(download_router)
app.include_router(auth_router)
app.include_router(emergency_router)
app.include_router(semantic_router)
app.include_router(ai_emergency_router)
app.include_router(chatbot_router)
app.include_router(sos_router)
app.include_router(contacts_router)

@app.get("/")
async def root():
    return {
        "message": "RoadSoS Backend Running"
    }