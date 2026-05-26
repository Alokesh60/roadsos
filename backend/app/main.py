from fastapi import FastAPI

from app.core.firebase_admin import *

from app.middleware.cors import (
    setup_cors
)

from app.db.sqlite_db import (
    initialize_database
)

from app.services.sqlite_service import (
    get_all_services
)

# =====================================
# API ROUTERS
# =====================================

from app.api.health import (
    router as health_router
)

from app.api.nearby import (
    router as nearby_router
)

from app.api.search import (
    router as search_router
)

from app.api.download import (
    router as download_router
)

from app.api.emergency import (
    router as emergency_router
)

from app.api.ai_emergency import (
    router as ai_emergency_router
)

from app.api.chatbot import (
    router as chatbot_router
)

from app.api.sos import (
    router as sos_router
)

from app.api.contacts import (
    router as contacts_router
)

from app.api.live_location import (
    router as live_location_router
)

from app.api.test_twilio import (
    router as test_twilio_router
)

from tests.test_auth import (
    router as test_auth_router
)


# =====================================
# FASTAPI APP
# =====================================

app = FastAPI(

    title="RoadSOS API",

    description=(
        "Emergency Response "
        "and Offline Safety Platform"
    ),

    version="2.0.0"
)


# =====================================
# STARTUP EVENT
# =====================================

@app.on_event("startup")
async def startup_event():

    print(
        "\n[Startup] Initializing database..."
    )

    initialize_database()

    print(
        "[Startup] Database initialized."
    )

    print(
        "\n[Startup] Loading service points..."
    )

    services = get_all_services()

    print(
        f"[Startup] Loaded "
        f"{len(services)} service points."
    )

    print(
        "\n[Startup] RoadSOS backend ready.\n"
    )


# =====================================
# CORS
# =====================================

setup_cors(app)


# =====================================
# ROUTERS
# =====================================

app.include_router(health_router)

app.include_router(nearby_router)

app.include_router(search_router)

app.include_router(download_router)

app.include_router(emergency_router)

app.include_router(ai_emergency_router)

app.include_router(chatbot_router)

app.include_router(sos_router)

app.include_router(contacts_router)

app.include_router(test_auth_router)

app.include_router(live_location_router)

app.include_router(test_twilio_router)


# =====================================
# ROOT
# =====================================

@app.get("/")
async def root():

    return {

        "success": True,

        "message":
            "RoadSOS Backend Running",

        "version":
            "2.0.0",

        "features": [

            "WhatsApp SOS",

            "Nearby User Broadcast",

            "Offline Emergency Database",

            "Google Places Integration",

            "Disaster Alert Support"
        ]
    }