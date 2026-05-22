from fastapi import APIRouter, Depends

from app.dependencies import verify_token

router = APIRouter()


@router.get("/me")
async def get_me(
    user=Depends(verify_token)
):

    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "phone": user.phone
        }
    }

from fastapi import HTTPException
from pydantic import BaseModel

from app.db.client import supabase


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(data: LoginRequest):

    try:

        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })

        session = response.session

        return {
            "success": True,
            "access_token": session.access_token,
            "refresh_token": session.refresh_token
        }

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )