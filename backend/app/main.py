from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.nearby import router as nearby_router
from app.api.search import router as search_router
from app.api.download import router as download_router
from app.api.auth import router as auth_router
from app.middleware.cors import setup_cors
from app.api.emergency import router as emergency_router
from app.api.semantic import router as semantic_router

app = FastAPI(
    title="RoadSoS API",
    description="Emergency Road Safety Backend",
    version="1.0.0"
)
setup_cors(app)

app.include_router(health_router)
app.include_router(nearby_router)
app.include_router(search_router)
app.include_router(download_router)
app.include_router(auth_router)
app.include_router(emergency_router)
app.include_router(semantic_router)


@app.get("/")
async def root():
    return {
        "message": "RoadSoS Backend Running"
    }