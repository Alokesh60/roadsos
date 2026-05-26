from fastapi import (

    APIRouter,
    Depends
)

from app.dependencies.auth_dependency import (
    get_current_user
)

router = APIRouter()


@router.get("/test-auth")

async def test_auth(

    user = Depends(get_current_user)

):

    return {

        "success": True,

        "uid": user["uid"],

        "email": user.get("email")
    }