import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies.auth_dependency import get_current_user
from app.schemas.chat_schema import ChatRequest

router = APIRouter()

AI_MODULE_URL = os.getenv("AI_MODULE_URL")
AI_MODULE_API_KEY = os.getenv("AI_MODULE_API_KEY")

@router.post("/chat")
async def chat_proxy(
    request: ChatRequest,
    user = Depends(get_current_user)
):
    if not AI_MODULE_URL:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI Module URL is not configured on the backend."
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{AI_MODULE_URL}/chat",
                headers={
                    "Authorization": f"Bearer {AI_MODULE_API_KEY}"
                },
                json=request.model_dump()
            )
            
            if response.status_code == 401 or response.status_code == 403:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Backend authentication to AI Module failed."
                )
                
            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI Module request timed out."
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"AI Module returned error: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI Module is currently unavailable: {str(e)}"
        )
