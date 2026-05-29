from fastapi import FastAPI

from app.core.firebase_admin import (
    initialize_firebase
)

from app.middleware.cors import (
    setup_cors
)

# =====================================
# API ROUTERS
# =====================================

from app.api.health import (
    router as health_router
)

from app.api.sos import (
    router as sos_router
)


# =====================================
# FASTAPI APP
# =====================================

app = FastAPI(

    title="RoadSOS API",

    description=(
        "RoadSOS Emergency Backend"
    ),

    version="3.0.0"
)


# =====================================
# STARTUP EVENT
# =====================================

@app.on_event("startup")
async def startup_event():

    # =================================
    # FIREBASE INITIALIZATION
    # =================================

    initialize_firebase()

    print(
        "\n[Startup] RoadSOS backend starting..."
    )

    print(
        "[Startup] Firebase initialized."
    )

    print(
        "[Startup] Backend ready.\n"
    )


# =====================================
# CORS
# =====================================

setup_cors(app)


# =====================================
# ROUTERS
# =====================================

app.include_router(health_router)

app.include_router(sos_router)


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
            "3.0.0",

        "architecture": {

            "frontend":
                (
                    "Android handles "
                    "Maps, Places, Routing"
                ),

            "backend":
                (
                    "SOS orchestration "
                    "and notifications"
                ),

            "ai_module":
                "Emergency AI guidance"
        },

        "features": [

            "SOS Alerts",

            "Twilio Notifications",

            "AI Emergency Guidance",

            "Firebase Authentication"
        ]
    }