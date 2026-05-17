from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.services.offline_service import export_sqlite_database

router = APIRouter()


@router.get("/download/db")
async def download_database():

    db_path = export_sqlite_database()

    return FileResponse(
        path=db_path,
        filename="roadsos_offline.db",
        media_type="application/octet-stream"
    )