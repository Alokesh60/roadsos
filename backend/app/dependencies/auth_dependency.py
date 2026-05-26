# from fastapi import (

#     Header,

#     HTTPException
# )

# from app.services.firebase_auth_service import (
#     verify_firebase_token
# )


# def get_current_user(

#     authorization: str = Header(None)

# ):

#     if not authorization:

#         raise HTTPException(

#             status_code=401,

#             detail="Authorization header missing"
#         )

#     try:

#         token = authorization.split(
#             "Bearer "
#         )[1]

#         decoded_token = (
#             verify_firebase_token(
#                 token
#             )
#         )

#         return decoded_token

#     except Exception as e:

#         raise HTTPException(

#             status_code=401,

#             detail=f"Invalid token: {e}"
#         )


def get_current_user():

    return {

        "uid": "test-user-001",

        "email": "alakesh@roadsos.com",

        "name": "Alakesh Boro"
    }