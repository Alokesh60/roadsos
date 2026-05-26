from fastapi import (
    APIRouter
)

from fastapi.responses import (
    FileResponse,
    JSONResponse
)

import os
import json

router = APIRouter()


# =====================================
# DOWNLOAD SQLITE DATABASE
# =====================================

@router.get("/download/db")

async def download_database():

    db_path = "roadsos.db"

    if not os.path.exists(db_path):

        return JSONResponse(

            status_code=404,

            content={

                "success": False,

                "message":
                    "Database file not found"
            }
        )

    return FileResponse(

        path=db_path,

        filename="roadsos.db",

        media_type="application/octet-stream"
    )


# =====================================
# DOWNLOAD EMERGENCY SEED
# =====================================

@router.get("/emergency-data")

async def download_emergency_data():

    seed_path = "emergency_seed.json"

    # =============================
    # OFFLINE FALLBACK
    # =============================

    if not os.path.exists(seed_path):

        fallback_data = {

            "service_points": [],

            "emergency_numbers": [],

            "chatbot_intents": [],

            "nh_corridors": []
        }

        return fallback_data

    # =============================
    # RETURN GENERATED JSON
    # =============================

    with open(

        seed_path,

        "r",

        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return {

        "success": True,

        "data": data
    }