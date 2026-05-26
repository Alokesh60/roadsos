from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Temporary authentication middleware.

    Current status:
    - Supabase auth removed
    - Firebase auth migration in progress
    - Returns mock authenticated user for development/testing

    TODO:
    Replace with Firebase token verification using:
    firebase_admin.auth.verify_id_token()
    """

    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authorization token missing"
        )

    # Temporary mock user
    return {
        "uid": "test-user-001",
        "email": "alakesh@roadsos.com",
        "name": "Alakesh Boro"
    }