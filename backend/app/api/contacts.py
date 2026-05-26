from fastapi import APIRouter

from app.schemas.contact_schema import (
    ContactCreate
)

from app.services.contact_service import (

    create_contact,

    get_contacts,

    delete_contact
)

router = APIRouter()


@router.post("/contacts")

async def add_contact(
    request: ContactCreate
):

    result = create_contact(
        request.dict()
    )

    return {

        "success": True,

        "data": result
    }


@router.get("/contacts/{user_id}")

async def fetch_contacts(
    user_id: str
):

    result = get_contacts(
        user_id
    )

    return {

        "success": True,

        "count": len(result),

        "data": result
    }


@router.delete("/contacts/{contact_id}")

async def remove_contact(
    contact_id: int
):

    result = delete_contact(
        contact_id
    )

    return {

        "success": True,

        "deleted": result
    }